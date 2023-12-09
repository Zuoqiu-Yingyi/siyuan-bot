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

import botpy
from botpy import logging
from botpy.audio import Audio
from botpy.audio import PublicAudio
from botpy.channel import Channel
from botpy.forum import Thread, OpenThread
from botpy.guild import Guild
from botpy.interaction import Interaction
from botpy.message import C2CMessage
from botpy.message import Message, DirectMessage, GroupMessage
from botpy.message import MessageAudit
from botpy.reaction import Reaction
from botpy.types.forum import Post, Reply, AuditResult
from botpy.user import Member

from type import result as T_result


class SiyuanBotClient(botpy.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._log = logging.get_logger()

    async def on_ready(self):
        self._log.info(f"robot [{self.robot.name}] on_ready!")

    async def _log_post_result(
        self,
        result: T_result.PostGroupMessageResult,
    ):
        self._log.debug(f"[siyuan] post_group_message: {result.get('msg')}")
        match result.get("msg"):
            case "success":
                pass
            case _:
                self._log.warn(f"[siyuan] post_group_message: {result}")

    # REF: https://github.com/tencent-connect/botpy/blob/master/docs/事件监听.md
    # REF: https://bot.q.qq.com/wiki/develop/pythonsdk/websocket/listen_events.html

    # region forums (私域) 论坛事件

    async def on_forum_thread_create(self, thread: Thread):
        """
        论坛主题创建事件
        """
        self._log.debug(f"[siyuan] on_forum_thread_create: {thread}")

    async def on_forum_thread_update(self, thread: Thread):
        """
        论坛主题更新事件
        """
        self._log.debug(f"[siyuan] on_forum_thread_update: {thread}")

    async def on_forum_thread_delete(self, thread: Thread):
        """
        论坛主题删除事件
        """
        self._log.debug(f"[siyuan] on_forum_thread_delete: {thread}")

    async def on_forum_post_create(self, post: Post):
        """
        论坛帖子创建事件
        """
        self._log.debug(f"[siyuan] on_forum_post_create: {post}")

    async def on_forum_post_delete(self, post: Post):
        """
        论坛帖子删除事件
        """
        self._log.debug(f"[siyuan] on_forum_post_delete: {post}")

    async def on_forum_reply_create(self, reply: Reply):
        """
        论坛评论创建事件
        """
        self._log.debug(f"[siyuan] on_forum_reply_create: {reply}")

    async def on_forum_reply_delete(self, reply: Reply):
        """
        论坛评论删除事件
        """
        self._log.debug(f"[siyuan] on_forum_reply_delete: {reply}")

    async def on_forum_publish_audit_result(self, audit: AuditResult):
        """
        论坛评论审核通过事件
        """
        self._log.debug(f"[siyuan] on_forum_publish_audit_result: {audit}")

    # endregion forums

    # region guild_messages (私域) 消息事件

    async def on_message_create(self, message: Message):
        """
        频道发送消息事件
        """
        self._log.debug(f"[siyuan] on_message_create: {message}")

    async def on_message_delete(self, message: Message):
        """
        频道删除（撤回）消息事件
        """
        self._log.debug(f"[siyuan] on_message_delete: {message}")

    # endregion guild_messages

    # region audio_action 音频事件

    async def on_audio_start(self, audio: Audio):
        """
        音频播放开始事件
        """
        self._log.debug(f"[siyuan] on_audio_start: {audio}")

    async def on_audio_finish(self, audio: Audio):
        """
        音频播放结束事件
        """
        self._log.debug(f"[siyuan] on_audio_finish: {audio}")

    async def on_audio_on_mic(self, audio: Audio):
        """
        上麦事件
        """
        self._log.debug(f"[siyuan] on_audio_on_mic: {audio}")

    async def on_audio_off_mic(self, audio: Audio):
        """
        下麦事件
        """
        self._log.debug(f"[siyuan] on_audio_off_mic: {audio}")

    # endregion audio_action

    # region audio_or_live_channel_member 音视频 & 直播频道

    async def on_audio_or_live_channel_member_enter(self, media: PublicAudio):
        """
        用户进入音视频/直播子频道
        """
        self._log.debug(f"[siyuan] on_audio_or_live_channel_member_enter: {media}")

    async def on_audio_or_live_channel_member_exit(self, media: PublicAudio):
        """
        用户离开音视频/直播子频道
        """
        self._log.debug(f"[siyuan] on_audio_or_live_channel_member_exit: {media}")

    # endregion audio_or_live_channel_member

    # region direct_message 私信事件

    async def on_direct_message_create(self, message: DirectMessage):
        """
        频道发送私信消息事件
        """
        # self._log.debug(f"[siyuan] on_direct_message_create: {message}")
        self._log.info(f"[siyuan] on_direct_message_create: {message.content}")

        # 等价于 message._api.post_message(channel_id=message.channel_id, msg_id=message.id, content)
        result = await message._api.post_dms(
            guild_id=message.guild_id,
            msg_id=message.id,
            content=f"收到频道私信:\n{message.content}",
        )

        self._log_post_result(result)

    async def on_direct_message_delete(self, message: DirectMessage):
        """
        频道删除（撤回）消息事件
        """
        self._log.debug(f"[siyuan] on_direct_message_delete: {message}")

    # endregion direct_message

    # region guild_members 频道成员事件

    async def on_guild_member_add(self, member: Member):
        """
        频道成员加入事件
        """
        self._log.debug(f"[siyuan] on_guild_member_add: {member}")

    async def on_guild_member_update(self, member: Member):
        """
        频道成员资料更新事件
        """
        self._log.debug(f"[siyuan] on_guild_member_update: {member}")

    async def on_guild_member_remove(self, member: Member):
        """
        频道成员退出事件
        """
        self._log.debug(f"[siyuan] on_guild_member_remove: {member}")

    # endregion guild_members

    # region guild_message_reactions 消息互动事件

    async def on_message_reaction_add(self, reaction: Reaction):
        """
        频道消息添加表情事件
        """
        self._log.debug(f"[siyuan] on_message_reaction_add: {reaction}")

    async def on_message_reaction_remove(self, reaction: Reaction):
        """
        频道消息删除表情事件
        """
        self._log.debug(f"[siyuan] on_message_reaction_remove: {reaction}")

    # endregion guild_message_reactions

    # region guilds 频道事件

    async def on_guild_create(self, guild: Guild):
        """
        机器人加入频道事件
        """
        self._log.debug(f"[siyuan] on_guild_create: {guild}")

    async def on_guild_update(self, guild: Guild):
        """
        频道资料变更事件
        """
        self._log.debug(f"[siyuan] on_guild_update: {guild}")

    async def on_guild_delete(self, guild: Guild):
        """
        机器人退出频道事件
        """
        self._log.debug(f"[siyuan] on_guild_delete: {guild}")

    async def on_channel_create(self, channel: Channel):
        """
        子频道创建事件
        """
        self._log.debug(f"[siyuan] on_channel_create: {channel}")

    async def on_channel_update(self, channel: Channel):
        """
        子频道更新事件
        """
        self._log.debug(f"[siyuan] on_channel_update: {channel}")

    async def on_channel_delete(self, channel: Channel):
        """
        子频道删除事件
        """
        self._log.debug(f"[siyuan] on_channel_delete: {channel}")

    # endregion guilds

    # region interaction 互动事件

    async def on_interaction_create(self, interaction: Interaction):
        """
        互动私信消息事件
        """
        self._log.debug(f"[siyuan] on_interaction_create: {interaction}")

    # endregion interaction

    # region message_audit 消息审核事件

    async def on_message_audit_pass(self, audit: MessageAudit):
        """
        消息审核通过事件
        """
        self._log.debug(f"[siyuan] on_message_audit_pass: {audit}")

    async def on_message_audit_reject(self, audit: MessageAudit):
        """
        消息审核未通过事件
        """
        self._log.debug(f"[siyuan] on_message_audit_reject: {audit}")

    # endregion message_audit

    # region open_forum_event 开放论坛消息

    async def on_open_forum_thread_create(self, thread: OpenThread):
        """
        开放论坛主题创建事件
        """
        self._log.debug(f"[siyuan] on_open_forum_thread_create: {thread}")

    async def on_open_forum_thread_update(self, thread: OpenThread):
        """
        开放论坛主题更新事件
        """
        self._log.debug(f"[siyuan] on_open_forum_thread_update: {thread}")

    async def on_open_forum_thread_delete(self, thread: OpenThread):
        """
        开放论坛主题删除事件
        """
        self._log.debug(f"[siyuan] on_open_forum_thread_delete: {thread}")

    async def on_open_forum_post_create(self, thread: OpenThread):
        """
        开放论坛帖子创建事件
        """
        self._log.debug(f"[siyuan] on_open_forum_post_create: {thread}")

    async def on_open_forum_post_delete(self, thread: OpenThread):
        """
        开放论坛帖子删除事件
        """
        self._log.debug(f"[siyuan] on_open_forum_post_delete: {thread}")

    async def on_open_forum_reply_create(self, thread: OpenThread):
        """
        开放论坛评论创建事件
        """
        self._log.debug(f"[siyuan] on_open_forum_reply_create: {thread}")

    async def on_open_forum_reply_delete(self, thread: OpenThread):
        """
        开放论坛评论删除事件
        """
        self._log.debug(f"[siyuan] on_open_forum_reply_delete: {thread}")

    # endregion open_forum_event

    # region public_guild_messages 频道 @ 消息事件

    async def on_at_message_create(self, message: Message):
        """
        频道 @机器人 消息事件
        """
        # self._log.debug(f"[siyuan] on_at_message_create: {message}")
        self._log.info(f"[siyuan] on_at_message_create: {message.content}")

        # 等价于 message._api.post_message(channel_id=message.channel_id, msg_id=message.id, content)
        result = await message.reply(
            content=f"收到频道消息:\n{message.content}",
        )

        self._log_post_result(result)

    async def on_public_message_delete(self, message: Message):
        """
        频道删除（撤回）消息事件
        """
        self._log.debug(f"[siyuan] on_public_message_delete: {message}")

    # endregion public_guild_messages

    # region public_messages 群/私聊消息事件

    async def on_c2c_message_create(self, message: C2CMessage):
        """
        私聊消息事件 (企业开发者)
        """
        self._log.debug(f"[siyuan] on_c2c_message_create: {message}")

    async def on_group_at_message_create(self, message: GroupMessage):
        """
        群 @ 消息事件
        """
        # self._log.debug(f"[siyuan] on_group_at_message_create: {message}")
        self._log.info(f"[siyuan] on_group_at_message_create: {message.content}")
        result = await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,
            msg_id=message.id,
            content=f"收到群消息:\n{message.content}",
        )
        self._log_post_result(result)

    # endregion public_messages
