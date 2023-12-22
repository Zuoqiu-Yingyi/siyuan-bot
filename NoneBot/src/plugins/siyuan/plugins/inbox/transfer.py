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

import re
import typing as T

import nonebot.adapters.onebot.v11 as ob
import nonebot.adapters.qq as qq
import nonebot.adapters.qq.models as models

from ...client import Client
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

hyperlink_pattern = re.compile(r"(?<=^|\s)(https?://[^\s]+)(?=\s|$)")


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
            message: 消息片段列表
            mode: 收集箱模式

        Returns:
            markdown: Markdown 文本
            files: 上传的文件列表
        """

        # TODO: 按照类型获取所有的资源消息片段
        # TODO: 批量下载资源文件到本地并上传至收集箱
        # TODO: 按照类型转换消息片段为 Markdown

    def text(
        self,
        segment: ob.MessageSegment | qq.MessageSegment,
    ) -> str:
        """将纯文本消息片段转换为 Markdown 文本

        Args:
            segment: [纯文本消息片段](https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#纯文本)

        Returns:
            markdown: Markdown 文本
        """

        # 超链接替换为 Markdown 格式
        text = segment.data.get("text")
        markdown = hyperlink_pattern.sub(r"[\1](<\1>)", text)

        return markdown

    def face(
        self,
        segment: ob.MessageSegment,
    ) -> str:
        """将表情消息片段转换为 Markdown 文本

        Args:
            segment: [表情消息片段](https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#纯文本)

        Returns:
            markdown: Markdown 文本
        """

        face_id = segment.data.get("id")
        return self._emoji(face_id)

    def emoji(
        self,
        segment: qq.message.Emoji,
    ) -> str:
        """将表情消息片段转换为 Markdown 文本

        Args:
            segment: 表情消息片段

        Returns:
            markdown: Markdown 文本
        """

        emoji_id = segment.data.id
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
        return f"<kbd>#{channel_id}</kbd>"

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
