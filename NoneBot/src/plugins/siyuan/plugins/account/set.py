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
from nonebot.adapters.onebot.v11 import (
    Bot,
    MessageEvent,
    Message,
)

accound_link = on_command(
    cmd="set",
    aliases={
        "设置",
    },
    block=True,
)


@accound_link.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
    command_args: Message = CommandArg(),
):
    # REF: https://nonebot.dev/docs/tutorial/event-data#%E4%BD%BF%E7%94%A8%E4%BE%9D%E8%B5%96%E6%B3%A8%E5%85%A5
    # 纯文本消息仅有一个消息片段, args 会移除消息中的命令部分与之前的空白字符
    if args := command_args.extract_plain_text():
        # TODO: 
        await accound_link.finish(f"参数:\n{args}")
    else:
        await accound_link.finish("参数格式错误")
