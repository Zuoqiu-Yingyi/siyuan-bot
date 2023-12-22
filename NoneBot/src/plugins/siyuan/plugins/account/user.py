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

from email import message
from functools import partial
from urllib.parse import (
    ParseResult,
    urlparse,
)

from nonebot import on_command
from nonebot.rule import to_me
import nonebot.adapters.onebot.v11 as ob
import nonebot.adapters.qq as qq
import nonebot.adapters.qq.models as models

from ... import data
from ...data import InboxMode
from ...reply import reply

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
    bot: ob.Bot | qq.Bot,
    event: ob.MessageEvent | qq.MessageEvent,
):
    reply_ = partial(
        reply,
        bot=bot,
        event=event,
        matcher=current_user,
    )
    user_id = event.get_user_id()
    account = data.getAccount(user_id)
    match account.inbox.mode:
        case InboxMode.none:
            mode = "<未设置>"
        case InboxMode.cloud:
            mode = "云收集箱"
        case InboxMode.service:
            mode = "思源收集箱"

    baseURI = (
        desensitizeString(account.service.baseURI)  #
        if len(account.service.baseURI) == 0
        else desensitizeURI(urlparse(account.service.baseURI))
    )
    lines = [
        f"- 当前用户 (id): {account.id}",
        f"- 收集箱 (inbox)",
        f"  - 是否已启用 (enable): {account.inbox.enable}",
        f"  - 默认模式 (mode): {mode}",
        f"- 云服务 (cloud):",
        f"  - 链滴 API 令牌 (token): {desensitizeString(account.cloud.token)}",
        f"- 内核服务 (service):",
        f"  - 内核服务地址 (baseURI): {baseURI}",
        f"  - 内核服务令牌 (token): {desensitizeString(account.service.token)}",
        f"  - 资源文件目录 (assets): {account.service.assets}",
        f"  - 笔记本 ID (notebook): {desensitizeString(account.service.notebook)}",
    ]

    match event:
        case qq.QQMessageEvent():  # 群聊/单聊
            await reply_(qq.MessageSegment.text("\n".join(lines)))
        case qq.GuildMessageEvent():  # 频道/私信
            ## Markdown 消息模板需要申请
            # await reply_(message=qq.MessageSegment.markdown(message))
            await reply_(
                message=qq.MessageSegment.embed(
                    qq.message.MessageEmbed(
                        title=event.author.username,
                        prompt=f"用户信息 [{event.author.username}]",
                        description=f"用户 [@{event.author.username}] 绑定的信息",
                        # thumbnail={
                        #     "url": event.author.avatar,
                        # },
                        ## fields 中的 name 不能为空字符串, 否则消息卡片会显示为空白
                        fields=[models.MessageEmbedField(name=name) for name in lines],
                    )
                ),
                reference=False,
            )
