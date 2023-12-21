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
from nonebot.rule import to_me

from ....siyuan import pgp

public_key = on_command(
    cmd="key",
    aliases={
        "公钥",
        "PGP公钥",
    },
    rule=to_me(),
    block=True,
    priority=1,
)


@public_key.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
):
    await public_key.finish(f"PGP 公钥：\n\n{pgp.public_key}")
