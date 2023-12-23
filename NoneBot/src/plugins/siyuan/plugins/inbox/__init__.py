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

from functools import partial
from nonebot import on_message
from nonebot.plugin import PluginMetadata
import nonebot.adapters.onebot.v11 as ob
import nonebot.adapters.qq as qq

from ... import data
from ...client import Client
from ...data import InboxMode
from ...reply import reply
from . import (
    middleware,
    settings,
)
from .transfer import Transfer

usage = """\
/inbox, /收集箱
    管理收集箱功能
    使用命令 /help inbox 查看更多信息
---
其他内容将会转发至收集箱
"""

__plugin_meta__ = PluginMetadata(
    name="inbox",
    description="收集箱",
    usage=usage,
    supported_adapters={"onebot.v11", "qq"},
)

# 默认收集箱
inbox_default = on_message(
    priority=3,
)


@inbox_default.handle()
async def _(
    bot: ob.Bot | qq.Bot,
    event: ob.MessageEvent | qq.MessageEvent,
):
    reply_ = partial(
        reply,
        bot=bot,
        event=event,
        matcher=inbox_default,
    )

    # 判断当前默认收集箱方案
    user_id = event.get_user_id()
    account = data.getAccount(user_id)
    if account.inbox.enable:
        client = Client.new(account)
        transfer = Transfer(client)
        content: str

        # 解析消息
        try:
            content = await transfer.msg2md(
                mode=account.inbox.mode,
                message=event.get_message(),
                event=event,
            )
        except Exception as e:
            await reply_("解析消息异常")
            # await reply_(f"解析消息异常：\n{e}")

        # 上传收集箱内容
        inbox_mode: str
        try:
            match account.inbox.mode:
                case InboxMode.none:
                    inbox_mode = "未设置默认收集箱"
                case InboxMode.cloud:
                    await client.addCloudShorthand(content=content)
                    inbox_mode = "云收集箱"
                case InboxMode.service:
                    inbox_mode = "思源收集箱"
        except Exception as e:
            await reply_(f"上传收集箱异常：\n{e}")
        await reply_(f"已加入收集箱: {inbox_mode}")
    else:
        await reply_("收集箱未启用")
