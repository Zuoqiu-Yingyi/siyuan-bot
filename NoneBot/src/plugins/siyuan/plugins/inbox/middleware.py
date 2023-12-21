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

from nonebot import on_message
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.rule import to_me

# 消息中间件
inbox_message_middleware = on_message(
    rule=to_me(),
    priority=2,
    block=False,
)

# 频道消息中的表情符号 `<emoji:289>`
guild_emoji_pattern = re.compile(r"\<emoji:(?P<id>\d+)\>")

# 群聊消息中的表情符号 `<faceType=3,faceId="289",ext="eyJ0ZXh0Ijoi552B55y8In0=">`
group_emoji_pattern = re.compile(r'\<faceType=(?P<type>\d+),faceId="(?P<id>\d+)",ext="(?P<ext>[0-9a-zA-Z+/]*={0,2})"\>')


@inbox_message_middleware.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
):
    message = Message()
    for segment in event.get_message():
        match segment.type:
            case "text":
                text = segment.data.get("text")
                matchs: T.List[re.Match]
                match event.real_message_type:
                    # 频道表情
                    case "guild" | "guild_private":
                        matchs = list(re.finditer(guild_emoji_pattern, text))

                    # 群聊表情
                    case "group" | "":
                        matchs = list(re.finditer(group_emoji_pattern, text))

                    case _:
                        matchs = []

                if len(matchs) == 0:
                    message.append(segment)
                else:
                    begin = 0
                    for match in matchs:
                        start = match.start()
                        if begin < start:
                            message.append(MessageSegment.text(text[begin:start]))
                        message.append(MessageSegment.face(int(match.group("id"))))
                        begin = match.end()
                    if begin < len(text):
                        message.append(MessageSegment.text(text[begin:]))
            case _:
                message.append(segment)
    event.message = message
