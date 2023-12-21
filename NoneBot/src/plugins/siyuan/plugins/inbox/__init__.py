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

from nonebot import on_message
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
)
from nonebot.plugin import PluginMetadata

from ... import data
from ...data import InboxMode
from . import (
    middleware,
    settings,
)

__plugin_meta__ = PluginMetadata(
    name="inbox",
    description="收集箱",
    usage="",
)

# 默认收集箱
inbox_default = on_message(
    priority=3,
)


@inbox_default.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
):
    # 判断当前默认收集箱方案
    user_id = event.user_id
    account = data.getAccount(user_id)
    if account.inbox.enable:
        match account.inbox.mode:
            case InboxMode.none:
                pass
            case InboxMode.cloud:
                pass
            case InboxMode.service:
                pass
    # TODO: 解析消息
