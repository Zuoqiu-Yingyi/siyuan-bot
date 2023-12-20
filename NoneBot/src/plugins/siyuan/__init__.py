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

from pathlib import Path

import nonebot
from nonebot import (
    require,
    get_driver,
)
from nonebot.plugin import PluginMetadata

from .pgp import PGP
from .data import Data
from .config import SiyuanConfig

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as store  # noqa: E402

PLUGIN_NAME = "siyuan"

__plugin_meta__ = PluginMetadata(
    name=PLUGIN_NAME,
    description="",
    type="application",
    usage="",
    config=SiyuanConfig,
    supported_adapters={"onebot.v11"},
)

# REF: https://nonebot.dev/docs/appendices/config#%E6%8F%92%E4%BB%B6%E9%85%8D%E7%BD%AE
global_config = get_driver().config
siyuan_config = SiyuanConfig.parse_obj(global_config)

# REF: https://nonebot.dev/docs/best-practice/data-storing
pgp_primary_file = store.get_config_file(
    PLUGIN_NAME,
    siyuan_config.siyuan_pgp_primary_file_name,
)
data_file = store.get_data_file(
    PLUGIN_NAME,
    siyuan_config.siyuan_data_file_name,
)

pgp = PGP(
    config=siyuan_config,
    pgp_primary_file=pgp_primary_file,
)

data = Data(data_file=data_file)

sub_plugins = nonebot.load_plugins(
    str(Path(__file__).parent.joinpath("plugins").resolve())
)
