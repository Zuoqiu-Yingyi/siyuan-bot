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

from typing import Type

from nonebot.internal.matcher import Matcher
import nonebot.adapters as nb
import nonebot.adapters.onebot.v11 as ob
import nonebot.adapters.qq as qq


async def reply(
    message: None | str | nb.Message | nb.MessageSegment,
    bot: ob.Bot | qq.Bot,
    event: ob.MessageEvent | qq.MessageEvent,
    matcher: Type[Matcher],
    reference: bool = True,
):
    """回复消息

    Args:
        message: 要发送的消息
        bot: 机器人对象
        event: 消息事件
        matcher: 处理器对象
        reference: 是否引用回复
    """

    message_: nb.Message
    match bot:
        case ob.Bot():
            message_ = ob.Message(message)
            if reference and isinstance(event, ob.MessageEvent):
                message_id = event.message_id
                message_.append(ob.MessageSegment.reply(id_=message_id))
        case qq.Bot():
            message_ = qq.Message(message)
            if reference and isinstance(event, qq.GuildMessageEvent):
                message_id = event.id
                message_.append(qq.MessageSegment.reference(reference=message_id))
        case _:
            raise ValueError("Unknown bot type")
    await matcher.finish(message_)
