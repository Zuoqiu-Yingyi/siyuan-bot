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

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
)

from ... import data
from ...data import InboxMode

current_user = on_command(
    cmd="user",
    aliases={
        "用户",
        "当前用户",
    },
    block=True,
)


def hide(secret: str) -> str:
    if len(secret) == 0:
        return "<未设置>"
    elif len(secret) <= 6:
        return "*" * len(secret)
    else:
        return f"{secret[0]}{'*' * (len(secret) - 2)}{secret[-1]}"


@current_user.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
):
    user_id = event.get_user_id()
    account = data.getAccount(user_id)
    match account.mode:
        case InboxMode.none:
            mode = "<未设置>"
        case InboxMode.cloud:
            mode = "云收集箱"
        case InboxMode.service:
            mode = "思源内核服务收集箱"
    await current_user.finish("\n".join([
        f"- 当前用户 ID: {account.id}",
        f"- 默认模式: {mode}",
        f"- 云收集箱:",
        f"  - 是否已启用: {account.cloud.enable}",
        f"  - 链滴 token: {hide(account.cloud.token)}",
        f"- 思源内核服务收集箱:",
        f"  - 是否已启用: {account.service.enable}",
        f"  - 内核服务地址: {hide(account.service.baseURI)}",
        f"  - 内核服务 token: {hide(account.service.token)}",
        f"  - 笔记本 ID: {hide(account.service.notebook)}",
    ]))
