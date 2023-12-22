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
from nonebot.params import CommandArg
from nonebot.rule import to_me
import nonebot.adapters.onebot.v11 as ob
import nonebot.adapters.qq as qq

from ... import data
from ...data import InboxMode
from ...reply import reply

inbox_settings = on_command(
    cmd="inbox",
    aliases={
        "收集箱",
    },
    rule=to_me(),
    block=True,
    priority=1,
)


@inbox_settings.handle()
async def _(
    bot: ob.Bot | qq.Bot,
    event: ob.MessageEvent | qq.MessageEvent,
    command_args: ob.Message | qq.Message = CommandArg(),
):
    user_id = event.get_user_id()
    account = data.getAccount(user_id)
    changed = False
    message: str
    if text := command_args.extract_plain_text():
        match text.lower():
            case "enable" | "true" | "on" | "开启" | "启用":
                account.inbox.enable = True
                changed = True
                message = "收集箱: 已开启"
            case "disable" | "false" | "off" | "关闭" | "禁用":
                account.inbox.enable = False
                changed = True
                message = "收集箱: 已关闭"
            case "0" | "none" | "无" | "未设置":
                account.inbox.mode = InboxMode.none
                changed = True
                message = "收集箱模式: 未设置"
            case "1" | "cloud" | "云" | "云服务" | "链滴" | "云收集箱":
                account.inbox.mode = InboxMode.cloud
                changed = True
                message = "收集箱模式: 云收集箱"
            case "2" | "service" | "思源" | "内核" | "服务" | "思源内核" | "思源服务" | "内核服务" | "思源收集箱":
                account.inbox.mode = InboxMode.service
                changed = True
                message = "收集箱模式: 思源收集箱"
            case _:
                message = f"未知参数: {text}"
    else:
        message = "命令无参数"

    if changed:
        data.updateAccount(account)
    await reply(
        message=message,
        bot=bot,
        event=event,
        matcher=inbox_settings,
    )
