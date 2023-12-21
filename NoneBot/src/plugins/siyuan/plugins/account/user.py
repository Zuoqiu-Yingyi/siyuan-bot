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

from urllib.parse import (
    ParseResult,
    urlparse,
)

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
)
from nonebot.rule import to_me

from ... import data
from ...data import InboxMode

current_user = on_command(
    cmd="user",
    aliases={
        "用户",
        "当前用户",
    },
    rule=to_me(),
    block=True,
    priority=1,
)


def hide(secret: str) -> str:
    return "*" * len(secret)


def desensitizeString(secret: str) -> str:
    if len(secret) == 0:
        return "<未设置>"
    elif len(secret) <= 6:
        return hide(secret)
    else:
        return f"{secret[0]}{hide(secret[1:-1])}{secret[-1]}"


def desensitizeURI(secret: ParseResult) -> str:
    return "".join(
        [
            hide(secret.scheme),
            "://",
            ".".join(map(hide, secret.hostname.split("."))),
            "" if secret.port is None else f":{hide(str(secret.port))}",
            "/".join(map(hide, secret.path.split("/"))),
        ]
    )


@current_user.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
):
    user_id = event.user_id
    account = data.getAccount(user_id)
    match account.mode:
        case InboxMode.none:
            mode = "<未设置>"
        case InboxMode.cloud:
            mode = "云收集箱"
        case InboxMode.service:
            mode = "思源内核服务收集箱"

    baseURI = (
        desensitizeString(account.service.baseURI)  #
        if len(account.service.baseURI) == 0
        else desensitizeURI(urlparse(account.service.baseURI))
    )

    print(baseURI)

    await current_user.finish(
        "\n".join(
            [
                f"当前用户 ID: {account.id}",
                f"",
                f"- 默认模式 (mode): {mode}",
                f"- 云收集箱 (cloud):",
                f"  - 是否已启用 (enable): {account.cloud.enable}",
                f"  - 链滴 API 令牌 (token): {desensitizeString(account.cloud.token)}",
                f"- 内核服务收集箱 (service):",
                f"  - 是否已启用 (enable): {account.service.enable}",
                f"  - 内核服务地址 (baseURI): {baseURI}",
                f"  - 内核服务令牌 (token): {desensitizeString(account.service.token)}",
                f"  - 笔记本 ID (notebook): {desensitizeString(account.service.notebook)}",
            ]
        )
    )
