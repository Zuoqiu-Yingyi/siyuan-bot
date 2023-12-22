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

import re

from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.rule import to_me
from pgpy.types import Armorable
import nonebot.adapters.onebot.v11 as ob
import nonebot.adapters.qq as qq

from ... import (
    data,
    pgp,
)
from ...data import InboxMode

accound_config = on_command(
    cmd="config",
    aliases={
        "配置",
    },
    rule=to_me(),
    block=True,
    priority=1,
)


def str2bool(s: str) -> bool:
    return s.lower() in ["true", "1"]


@accound_config.handle()
async def _(
    bot: ob.Bot | qq.Bot,
    event: ob.MessageEvent | qq.MessageEvent,
    command_args: ob.Message | qq.Message = CommandArg(),
):
    # REF: https://nonebot.dev/docs/tutorial/event-data#%E4%BD%BF%E7%94%A8%E4%BE%9D%E8%B5%96%E6%B3%A8%E5%85%A5
    # 纯文本消息仅有一个消息片段, args 会移除消息中的命令部分与之前的空白字符
    if text := command_args.extract_plain_text():
        text = re.sub(r"[\r\n]+", "\n", text)  # 删除连续的换行
        if Armorable.is_armor(text):
            try:
                while armor_match := pgp.armor_regex.search(text):
                    ciphertext = armor_match.group()
                    plaintext = pgp.decrypt(ciphertext)
                    text = text.replace(ciphertext, plaintext)
            except Exception as e:
                await accound_config.finish(f"解密失败: {e}")

        args = list(
            filter(
                lambda s: len(s) > 0,
                map(
                    lambda s: s.strip(),
                    text.splitlines(),
                ),
            )
        )
        user_id = event.get_user_id()
        command = args[0]
        match command:
            case "unbind" | "解绑":
                data.deleteAccount(user_id)
                await accound_config.finish(f"解绑账户 {user_id} 成功")
            case "help" | "帮助":
                await accound_config.finish(
                    "\n".join(
                        [
                            "/config help 获取命令帮助",
                            "/config unbind 解绑账户",
                            "/config set 设置配置字段",
                        ]
                    )
                )
            case "set" | "设置":
                account = data.getAccount(user_id)
                success: list[str] = []  # 设置成功的属性
                failure: list[str] = []  # 设置失败的属性
                # 明文配置
                line: str
                for line in args[1:]:
                    parts = list(
                        filter(
                            lambda s: len(s) > 0,
                            map(
                                lambda s: s.strip(),
                                line.split("=", 1),
                            ),
                        )
                    )
                    if len(parts) != 2:  # 排除无效配置
                        failure.append(line)
                        continue
                    (key, value) = parts
                    attrs = key.split("/")
                    match attrs[0]:
                        case attr if attr == "account" and len(attrs) > 1:
                            match attrs[1]:
                                case attr if attr == "inbox" and len(attrs) > 2:
                                    match attrs[2]:
                                        case attr if attr == "enable" and len(attrs) == 3:
                                            account.inbox.enable = str2bool(value)
                                            success.append(key)
                                        case attr if attr == "mode" and len(attrs) == 3:
                                            if value in ["none", "0"]:
                                                account.inbox.mode = InboxMode.none
                                                success.append(key)
                                            elif value in ["cloud", "1"]:
                                                account.inbox.mode = InboxMode.cloud
                                                success.append(key)
                                            elif value in ["service", "2"]:
                                                account.inbox.mode = InboxMode.service
                                                success.append(key)
                                            else:
                                                failure.append(key)
                                case attr if attr == "cloud" and len(attrs) > 2:
                                    match attrs[2]:
                                        case attr if attr == "token" and len(attrs) == 3:
                                            account.cloud.token = value
                                            success.append(key)
                                        case _:
                                            failure.append(key)
                                case attr if attr == "service" and len(attrs) > 2:
                                    match attrs[2]:
                                        case attr if attr == "baseURI" and len(attrs) == 3:
                                            account.service.baseURI = value
                                            success.append(key)
                                        case attr if attr == "token" and len(attrs) == 3:
                                            account.service.token = value
                                            success.append(key)
                                        case attr if attr == "assets" and len(attrs) == 3:
                                            if value.startswith("/assets/"):
                                                account.service.assets = value
                                                success.append(key)
                                            else:
                                                failure.append(key)
                                        case attr if attr == "notebook" and len(attrs) == 3:
                                            account.service.notebook = value
                                            success.append(key)
                                        case _:
                                            failure.append(key)
                                case _:
                                    failure.append(key)
                        case _:
                            failure.append(key)
                # 保存
                data.updateAccount(account)
                # 反馈
                await accound_config.finish(
                    "\n".join(
                        [
                            "设置成功:",
                            *success,
                            "",
                            "设置失败:",
                            *failure,
                        ]
                    )
                )
            case _:
                await accound_config.finish("未知参数: {command}")

    else:
        await accound_config.finish("参数格式错误")
