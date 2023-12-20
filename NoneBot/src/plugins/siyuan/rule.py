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

from nonebot.adapters.onebot.v11 import (
    MessageEvent,
)


def isGuildMessage(event: MessageEvent) -> bool:
    """判断是否为频道消息"""
    return event.message_type == "group" and event.real_message_type == "guild"


def isDirectMessage(event: MessageEvent) -> bool:
    """判断是在为频道私信消息"""
    return (
        event.message_type == "private" and event.real_message_type == "guild_private"
    )


def isGroupMessage(event: MessageEvent) -> bool:
    """判断是在为群聊消息"""
    return event.message_type == "group" and event.real_message_type == "group"
