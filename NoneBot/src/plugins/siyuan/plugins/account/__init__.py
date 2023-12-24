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

from nonebot.plugin import PluginMetadata

from . import (
    config,
    key,
    user,
)

usage = """\
/user, /用户
    查看当前用户信息
    使用命令 /help user 查看更多信息
---
/config, /配置
    更改当前用户配置
    使用命令 /help config 查看更多信息
---
/key, /公钥, /PGP公钥
    获取机器人的 PGP 公钥
    使用命令 /help key 查看更多信息
"""

__plugin_meta__ = PluginMetadata(
    name="account",
    description="账户管理",
    usage=usage,
    supported_adapters={"onebot.v11", "qq"},
)
