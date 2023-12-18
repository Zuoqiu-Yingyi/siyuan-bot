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
from ... import data

accound_config = on_command(
    cmd="config",
    aliases={
        "设置",
        "配置",
    },
    block=True,
)


@accound_config.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
    command_args: Message = CommandArg(),
):
    # REF: https://nonebot.dev/docs/tutorial/event-data#%E4%BD%BF%E7%94%A8%E4%BE%9D%E8%B5%96%E6%B3%A8%E5%85%A5
    # 纯文本消息仅有一个消息片段, args 会移除消息中的命令部分与之前的空白字符
    if text := command_args.extract_plain_text():
        args = filter(
            lambda s: len(s) != 0, map(lambda s: s.strip(), text.splitlines())
        )
        user_id = event.get_user_id()
        match len(args):
            case 1:
                command = args[0]
                match command:
                    case "unbind" | "解绑":
                        data.deleteAccount(user_id)
                        await accound_config.finish(f"解绑账户 {user_id} 成功")
                    case _:
                        await accound_config.finish("未知参数: {command}")

    else:
        await accound_config.finish("参数格式错误")
