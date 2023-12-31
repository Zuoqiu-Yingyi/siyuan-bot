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
from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
import nonebot.adapters.onebot.v11 as ob
import nonebot.adapters.qq as qq
import nonebot.adapters.qq.models as models

from ..reply import reply
from .account import usage as account_usage
from .inbox import usage as inbox_usage

usage = f"""\
/help, /帮助
    查看当前所有命令
---
/help [命令], /帮助 [命令]
    查看指定命令的使用方法
---
{account_usage}
---
{inbox_usage}\
"""

__plugin_meta__ = PluginMetadata(
    name="help",
    description="用户帮助",
    usage=usage,
    supported_adapters={"onebot.v11", "qq"},
)

help = on_command(
    cmd="help",
    aliases={
        "帮助",
    },
    rule=to_me(),
    block=True,
    priority=1,
)


@help.handle()
async def _(
    bot: ob.Bot | qq.Bot,
    event: ob.MessageEvent | qq.MessageEvent,
    command_args: ob.Message | qq.Message = CommandArg(),
):
    reply_ = partial(
        reply,
        bot=bot,
        event=event,
        matcher=help,
    )

    lines: list[str] = []
    if command := command_args.extract_plain_text():
        match command:
            case "user" | "用户":
                lines.extend(
                    [
                        (
                            "/user, /用户\n"  #
                            "  查看当前用户信息\n"  #
                            "  - 当前用户 ID\n"  #
                            "  - 收集箱功能状态与模式\n"  #
                            "  - 云收集箱 (链滴) 相关配置\n"  #
                            "  - 思源收集箱 (思源伺服) 相关配置\n"  #
                        )
                    ]
                )
            case "config" | "设置":
                lines.extend(
                    [
                        (
                            "/config reset, /配置 重置\n"  #
                            "  重置当前用户自定义配置项为默认值\n"  #
                        ),
                        (
                            "\n"  #
                            "/config set [新配置项列表], /配置 更改 [新配置项列表]\n"  #
                            "  更改当前用户的自定义设置\n"  #
                        ),
                        (
                            "  设置项格式：\n"  #
                            "    - 每行一项需要修改的配置项的键值对\n"  #
                            "    - 使用符号 = 分割配置项名称与值\n"  #
                        ),
                        (
                            "  注意事项：\n"  #
                            "    - 配置项键值对可以使用 PGP 加密以避免秘密信息的泄露\n"  #
                            "    - 机器人的 PGP 加密公钥可以使用命令 /key 获取\n"  #
                        ),
                        (
                            "  所有设置项：\n"  #
                            "    - /account/inbox/enable 收集箱状态\n"  #
                            "      - True: 开启; False: 关闭\n"  #
                        ),
                        (
                            "    - /account/inbox/mode 收集箱默认模式\n"  #
                            "      - 0: 未设置; 1: 云收集箱 (链滴); 2: 思源收集箱 (思源伺服)\n"  #
                        ),
                        (
                            "    - /account/cloud/token  云收集箱访问令牌 (token)\n"  #
                        ),
                        (
                            "    - /account/service/baseURI  思源内核服务 URL\n"  #
                            "    - /account/service/token  思源内核服务令牌 (token)\n"  #
                            "    - /account/service/assets  思源资源文件目录\n"  #
                            "    - /account/service/notebook  设置为收集箱的思源笔记本 ID\n"  #
                        ),
                        (
                            "  示例 1 (未使用 PGP 加密)：\n"  #
                            "    /config set\n"  #
                            "    /account/inbox/enable = True\n"  #
                            "    /account/inbox/mode = 1\n"  #
                            "    /account/cloud/token = kVvG9YBZauSnXJoy\n"  #
                        ),
                        (
                            "    /account/service/baseURI = http://***.***:6806\n"  #
                            "    /account/service/token = 9t6fqlbqz0gr9rac\n"  #
                            "    /account/service/assets = /assets/inbox/\n"  #
                            "    /account/service/notebook = 20210808180117-6v0mkxr\n"  #
                        ),
                        (
                            "  示例 2 (使用 PGP 加密)：\n"  #
                            "    /config set\n"  #
                            "    -----BEGIN PGP MESSAGE-----\n"  #
                            "    [ASCII-armored 格式 PGP 信息]\n"  #
                            "    -----END PGP MESSAGE-----\n"  #
                        ),
                    ]
                )
            case "key" | "公钥" | "PGP公钥":
                lines.extend(
                    [
                        (
                            "/key, /公钥, /PGP公钥\n"  #
                            "   获取机器人的 PGP 公钥\n"  #
                            "   该公钥可以在使用命令 /config set 修改用户配置时加密配置项中的敏感信息\n"  #
                        )
                    ]
                )
            case "inbox" | "收集箱":
                lines.extend(
                    [
                        (
                            "/inbox [命令], /收集箱 [命令]\n"  #
                            "   快捷开关/设置收集箱功能\n"  #
                        ),
                        (
                            "/inbox on/true/enable/开启/启用\n"  #
                            "   开启收集箱功能\n"  #
                        ),
                        (
                            "/inbox off/false/disable/关闭/禁用\n"  #
                            "   关闭收集箱功能\n"  #
                        ),
                        (
                            "/inbox 0/none/无/未设置\n"  #
                            "   重置收集箱模式为未设置\n"  #
                        ),
                        (
                            "/inbox 1/cloud/云/云收集箱\n"  #
                            "   收集箱模式设置为：云收集箱\n"  #
                        ),
                        (
                            "/inbox 2/service/思源/思源收集箱\n"  #
                            "   收集箱模式设置为：思源收集箱\n"  #
                        ),
                    ]
                )
            case _:
                lines.append(f"未知命令: {command}")

    else:
        lines = usage.split("\n---\n")

    match event:
        case qq.GuildMessageEvent():  # 频道/私信
            # 最长发送 24 行消息
            await reply_(
                message=qq.MessageSegment.embed(
                    qq.message.MessageEmbed(
                        title="思源小助手用户帮助",
                        prompt=f"命令 [{command}] 使用帮助",
                        fields=[models.MessageEmbedField(name=name) for name in lines],
                    )
                ),
                reference=False,
            )
        case _:
            lines.append("思源小助手用户帮助")
            await reply_("\n---\n".join(lines))
