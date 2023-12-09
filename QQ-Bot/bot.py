"""
 Copyright (C) 2023 Zuoqiu Yingyi
 
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.
 
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.
 
 You should have received a copy of the GNU Affero General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import botpy
from botpy.ext.cog_yaml import read
from client import SiyuanBotClient

# REF: https://github.com/tencent-connect/botpy/blob/master/examples/demo_at_reply.py
config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_guild_messages=True

    # 通过 kwargs，设置需要监听的事件通道
    intents = botpy.Intents(
        # 私域事件
        forums=False,
        guild_messages=False,

        # 公域事件
        audio_action=True,
        audio_or_live_channel_member=True,
        direct_message=True,
        guild_members=True,
        guild_message_reactions=True,
        guilds=True,
        interaction=True,
        message_audit=True,
        open_forum_event=True,
        public_guild_messages=True,
        public_messages=True,
    )
    client = SiyuanBotClient(intents=intents)
    client.run(
        appid=config["appid"],
        secret=config["secret"],
    )
