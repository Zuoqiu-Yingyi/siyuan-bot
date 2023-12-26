# Copyright (C) 2023 Zuoqiu Yingyi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pathlib import Path
import asyncio
import re
import typing as T
import uuid

from nonebot import logger
from pgpy.types import Armorable
import httpx
import nonebot.adapters.onebot.v11 as ob
import nonebot.adapters.qq as qq
import nonebot.adapters.qq.models as models

from ... import pgp
from ...client import Client, UploadResponse
from ...data import InboxMode


class File(object):
    name: T.Optional[str]  # 文件名
    origin_url: T.Optional[str]  # 文件原 URL (消息中的 URL)
    inbox_url: T.Optional[str]  # 文件新 URL (Markdown 中的 URL)

    def __init__(
        self,
        **kwargs,
    ):
        self.name = kwargs.get("name")
        self.origin_url = kwargs.get("origin_url")
        self.inbox_url = kwargs.get("inbox_url")


T_files = list[File]

hyperlink_pattern = re.compile(r"(?:(?<=\s)|^)(\w+://\S+)(?=\s|$)")


class Transfer(object):
    """将消息片段列表转换为 Markdown 文本"""

    __client: Client

    def __init__(
        self,
        client: Client,
    ):
        self.__client = client

    async def msg2md(
        self,
        mode: InboxMode,
        message: ob.Message | qq.Message,
        event: ob.MessageEvent | qq.MessageEvent,
    ) -> tuple[str, T_files]:
        """将消息转换为 Markdown 文本并上传相关资源

        [消息段类型](https://github.com/botuniverse/onebot-11/blob/master/message/segment.md)

        Args:
            mode: 收集箱模式
            message: 消息片段列表
            event: 消息事件

        Returns:
            markdown: Markdown 文本
            files: 上传的文件列表
        """

        # 资源文件转储
        await self.dump(message)

        # 按照类型转换消息片段为 Markdown
        match mode:
            case InboxMode.none:
                raise ValueError("未设置默认收集箱模式")
            case InboxMode.cloud | InboxMode.service:
                markdowns: list[str] = []
                for segment in message:
                    match segment.type:
                        case "text":
                            markdowns.append(self.text(segment))
                        case "image":
                            markdowns.append(self.image(segment))
                        case "audio" | "record":
                            markdowns.append(self.audio(segment))
                        case "video":
                            markdowns.append(self.video(segment))
                        case "face" | "emoji":
                            markdowns.append(self.emoji(segment))
                        case "at":
                            markdowns.append(self.at(segment))
                        case "mention_user":
                            match event:
                                case qq.message.GuildMessage():
                                    markdowns.append(self.mention_user(segment, event.mentions))
                                case _:
                                    markdowns.append(self.mention_user(segment))
                        case "mention_channel":
                            markdowns.append(self.mention_channel(segment))
                return "".join(markdowns)
            case _:
                raise NotImplementedError("未知的收集箱模式")

    def text(
        self,
        segment: ob.MessageSegment | qq.message.Text,
    ) -> str:
        """将纯文本消息片段转换为 Markdown 文本

        Args:
            segment: [纯文本消息片段](https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#纯文本)

        Returns:
            markdown: Markdown 文本
        """

        # 超链接替换为 Markdown 格式
        text = segment.data.get("text")
        if Armorable.is_armor(text):
            try:
                while armor_match := pgp.armor_regex.search(text):
                    ciphertext = armor_match.group()
                    plaintext = pgp.decrypt(ciphertext)
                    text = text.replace(ciphertext, plaintext)
            except Exception as e:
                raise ValueError(f"PGP 消息解密失败: \n{e}")
        markdown = hyperlink_pattern.sub(r"[\1](<\1>)", text)

        return markdown

    def image(
        self,
        segment: ob.MessageSegment | qq.message.Attachment,
    ) -> str:
        """将图片消息片段转换为 Markdown 文本

        消息片段中图片文件已经转储完成

        Args:
            segment: [图片消息片段](https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#图片)

        Returns:
            markdown: Markdown 文本
        """

        # 超链接替换为 Markdown 格式
        file_name = segment.data.get("file", f"{uuid.uuid4()}.image")
        file_url = segment.data.get("url")

        return f"![{file_name}]({file_url})"

    def audio(
        self,
        segment: ob.MessageSegment | qq.message.Attachment,
    ) -> str:
        """将音频消息片段转换为 Markdown 文本

        消息片段中音频文件已经转储完成

        Args:
            segment: [音频消息片段](https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#语音)

        Returns:
            markdown: Markdown 文本
        """

        # 超链接替换为 Markdown 格式
        file_url = segment.data.get("url")
        return f'<audio controls="controls" src="{file_url}"></audio>'

    def video(
        self,
        segment: ob.MessageSegment | qq.message.Attachment,
    ) -> str:
        """将视频消息片段转换为 Markdown 文本

        消息片段中视频文件已经转储完成

        Args:
            segment: [视频消息片段](https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#短视频)

        Returns:
            markdown: Markdown 文本
        """

        # 超链接替换为 Markdown 格式
        file_url = segment.data.get("url")
        return f'<video controls="controls" src="{file_url}"></video>'

    def emoji(
        self,
        segment: ob.MessageSegment | qq.message.Emoji,
    ) -> str:
        """将表情消息片段转换为 Markdown 文本

        Args:
            segment: [表情消息片段](https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#纯文本)

        Returns:
            markdown: Markdown 文本
        """

        emoji_id = segment.data.get("id")
        return self._emoji(emoji_id)

    def at(
        self,
        segment: ob.MessageSegment,
    ) -> str:
        """将 @ 消息片段转换为 Markdown 文本

        Args:
            segment: [@某人消息片段](https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#某人)

        Returns:
            markdown: Markdown 文本
        """

        user_id = segment.data.get("qq")
        return self._at(user_id)

    def mention_user(
        self,
        segment: qq.message.MentionUser,
        mentions: list[models.User] | None,
    ) -> str:
        """将提及用户消息片段转换为 Markdown 文本

        Args:
            segment: 提及用户消息片段

        Returns:
            markdown: Markdown 文本
        """

        user_id = segment.data.get("user_id")
        user_name: str = ""
        if mentions:
            for mention in mentions:
                if mention.id == user_id:
                    user_name = mention.username
        return self._at(user_id, user_name)

    def mention_channel(
        self,
        segment: qq.message.MentionChannel,
    ) -> str:
        """将提及子频道消息片段转换为 Markdown 文本

        Args:
            segment: 提及子频道消息片段

        Returns:
            markdown: Markdown 文本
        """

        channel_id = segment.data.get("channel_id")
        return f"<kbd>#&lt;{channel_id}&gt;</kbd>"

    def _at(
        self,
        id: str,
        name: str = "",
    ) -> str:
        """将 @ 转换为 Markdown 格式"""
        return f"<u>@{name}&lt;{id}&gt;</u>"

    def _emoji(
        self,
        id: str | str,
    ) -> str:
        """将指定 ID 对应的表情转换为思源表情"""
        id = int(id)
        if id >= 8192:  # Unicode emoji
            return chr(id)
        else:  # QQ emoji
            return f":qq-gif/s{id}:"

    async def _cloudDump(
        self,
        segment: ob.MessageSegment | qq.MessageSegment,
        file_type: T.Literal["image", "audio", "video"],
    ):
        """将消息中的资源文件转储到云收集箱"""
        file_name = segment.data.get("file")
        file_url = segment.data.get("url")
        try:
            file_path, file_name = await self.__client.download(
                url=file_url,
                type=file_type,
                name=file_name,
            )

            with file_path.open("rb") as f:
                response: httpx.Response = await self.__client.cloudUpload(files=[(file_name, f)])
                response_body: UploadResponse = response.json()
                file_cloud_url = response_body["data"]["succMap"][file_name]

            segment.data["file"] = file_name
            segment.data["url"] = file_cloud_url
        except Exception as e:
            logger.warning(f"转储资源文件失败: {e}")

    async def dump(
        self,
        message: ob.Message | qq.Message,
    ):
        """将消息中的资源文件转储到收集箱"""
        async with asyncio.TaskGroup() as group:
            for segment in message:
                match segment.type:
                    case "image":
                        group.create_task(self._cloudDump(segment, "image"))
                    case "audio" | "record":
                        group.create_task(self._cloudDump(segment, "audio"))
                    case "video":
                        group.create_task(self._cloudDump(segment, "video"))
                    case _:
                        pass
