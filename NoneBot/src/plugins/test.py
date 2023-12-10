"""
 Copyright (C) 2023 Zuoqiu Yingyi
 
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.
 
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.
 
 You should have received a copy of the GNU Affero General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters.qq import (
    Bot,
    # Event,
    MessageSegment,
    # MessageCreateEvent, # 文字子频道消息 用于私域机器人
    AtMessageCreateEvent,  # 文字子频道消息
    DirectMessageCreateEvent,  # 频道私聊消息
    GroupAtMessageCreateEvent,  # 群聊@消息
    C2CMessageCreateEvent,  # 私聊消息
)

test = on_command("test")


@test.handle()
async def _(
    bot: Bot,
    event: AtMessageCreateEvent
    | GroupAtMessageCreateEvent
    | DirectMessageCreateEvent
    | C2CMessageCreateEvent,
):
    """
    参数通过依赖注入方式传入，只有满足类型标注时才会调用处理事件，否则会跳过处理

    例如本函数只对 qq-adapter 的 bot 以及指定的两种类型的 event 有效

    常用的参数有：

    - `bot`: Bot 对象，用于发送消息等
    - `event`: Event 对象，消息事件

    """

    # 用户 ID
    logger.info(
        f"Sender: {event.get_user_id()}"
    )  # 发送者 ID，不同于 QQ 号，群聊与频道不同

    logger.debug(f"/text event:\n{event.json()}")
    # 群组 ID
    if isinstance(event, AtMessageCreateEvent):  # 频道消息
        logger.debug("频道消息")
        logger.info(f"Guild ID: {event.guild_id}")  # 频道 ID
        logger.info(f"Channel ID: {event.channel_id}")  # 子频道 ID
    elif isinstance(event, GroupAtMessageCreateEvent):  # 群聊消息
        logger.debug("群聊消息")
        logger.info(f"Group ID: {event.group_openid}")  # 群聊 OpenID
    elif isinstance(event, DirectMessageCreateEvent):  # 频道私信
        logger.debug("频道私信")
        logger.info(f"Guild ID: {event.guild_id}")  # 频道 ID
    elif isinstance(event, C2CMessageCreateEvent):  # 群聊私信
        logger.debug("群聊私信")
        logger.info(f"Author ID: {event.author.user_openid}")  # 用户 OpenID

    # 发送文本
    message = MessageSegment.text(event.content)
    result = await test.send(message)
    logger.debug(result)

    # # 发送图片
    # if isinstance(event, AtMessageCreateEvent):
    #     message = MessageSegment.file_image(Path("./example/image.png"))
    #     """
    #     只能用于频道，群聊无法发送本地图片
    #     """
    # else:
    #     message = MessageSegment.image("https://example.com/image.png")
    # await test.send(message)

    # # 发送私聊消息
    # if isinstance(event, AtMessageCreateEvent):
    #     # 主动发起频道私信：创建临时频道 -> 发送消息
    #     dms = await bot.post_dms(
    #         recipient_id=event.get_user_id(), source_guild_id=event.guild_id
    #     )
    #     assert dms.guild_id is not None
    #     await bot.post_dms_messages(guild_id=dms.guild_id, content="Hello World!")
