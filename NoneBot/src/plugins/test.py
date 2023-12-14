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


from nonebot import (
    on_command,
    on_message,
    on_metaevent,
    on_notice,
    on_request,
)
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import (
    Bot,
    MetaEvent,
    NoticeEvent,
    RequestEvent,
    PrivateMessageEvent,
    GroupMessageEvent,
)

meta = on_metaevent()
message = on_message()
notice = on_notice()
request = on_request()


# @meta.handle()
# async def _(
#     bot: Bot,
#     event: MetaEvent,
# ):
#     logger.debug(f"meta: {event.meta_event_type}\n{event.json()}")


@notice.handle()
async def _(
    bot: Bot,
    event: NoticeEvent,
):
    logger.debug(f"notice: {event.notice_type}\n{event.json()}")


@request.handle()
async def _(
    bot: Bot,
    event: RequestEvent,
):
    logger.debug(f"request: {event.request_type}\n{event.json()}")


@message.handle()
async def _(
    bot: Bot,
    event: PrivateMessageEvent | GroupMessageEvent,
):
    logger.debug(f"message: {event.message_type}\n{event.json()}")
