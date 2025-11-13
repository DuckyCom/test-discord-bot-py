import discord
import asyncio
import requests
from enum import Enum
from datetime import datetime
from typing import Optional, Dict
from dataclasses import dataclass
from collections import defaultdict

from .dataManager import fetch_table, SUPABASE_URL, HEADERS

class ChannelState(Enum):
    AVAILABLE = "available"
    CLAIMED = "claimed"
    USED = "used"
    CLOSING = "closing"

@dataclass
class ChannelData:
    channel_id: int
    guild_id: int
    state: str
    owner_id: Optional[int] = None
    claimed_at: Optional[str] = None
    last_activity: Optional[str] = None
    prompt_message_id: Optional[int] = None

    @classmethod
    def from_db(cls, data):
        return cls(
            channel_id=data['channel_id'],
            guild_id=data['guild_id'],
            state=data['state'],
            owner_id=data.get('owner_id'),
            claimed_at=data.get('claimed_at'),
            last_activity=data.get('last_activity'),
            prompt_message_id=data.get('prompt_message_id')
        )

    def to_db(self):
        return {
            'channel_id': self.channel_id,
            'guild_id': self.guild_id,
            'state': self.state,
            'owner_id': self.owner_id,
            'claimed_at': self.claimed_at,
            'last_activity': self.last_activity,
            'prompt_message_id': self.prompt_message_id
        }

@dataclass
class GuildConfig:
    guild_id: int
    available_category_id: int
    used_category_id: int
    activity_timeout: int = 300
    close_timeout: int = 20
    min_available: int = 2
    max_available: int = 5
    max_per_user: int = 1

    @classmethod
    def from_db(cls, data):
        return cls(
            guild_id=data['guild_id'],
            available_category_id=data['available_category_id'],
            used_category_id=data['used_category_id'],
            activity_timeout=data.get('activity_timeout', 300),
            close_timeout=data.get('close_timeout', 20),
            min_available=data.get('min_available', 2),
            max_available=data.get('max_available', 5),
            max_per_user=data.get('max_per_user', 1)
        )

    def to_db(self):
        return {
            'guild_id': self.guild_id,
            'available_category_id': self.available_category_id,
            'used_category_id': self.used_category_id,
            'activity_timeout': self.activity_timeout,
            'close_timeout': self.close_timeout,
            'min_available': self.min_available,
            'max_available': self.max_available,
            'max_per_user': self.max_per_user
        }

class channelManager:
    def __init__(self, client: discord.Client):
        self.client = client
        self.guild_configs: Dict[int, GuildConfig] = {}
        self.channels: Dict[int, ChannelData] = {}
        self.locks: Dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)
        self.scheduler_task: Optional[asyncio.Task] = None

    async def load_config(self):
        try:
            guilds_data = fetch_table('guilds')
            for guild_row in guilds_data:
                guild_id = guild_row['guild_id']
                self.guild_configs[guild_id] = GuildConfig.from_db(guild_row)
            channels_data = fetch_table('channels')
            for channel_row in channels_data:
                channel_id = channel_row['channel_id']
                self.channels[channel_id] = ChannelData.from_db(channel_row)
        except Exception as e:
            print(f"Error loading config from database: {e}")

    def save_channel(self, channel_data: ChannelData):
        url = f'{SUPABASE_URL}/rest/v1/channels?channel_id=eq.{channel_data.channel_id}'
        response = requests.patch(url, headers=HEADERS, json=channel_data.to_db(), timeout=10)
        if response.status_code not in [200, 204]:
            print(f"Error updating channel: {response.text}")

    def save_guild(self, guild_config: GuildConfig):
        url = f'{SUPABASE_URL}/rest/v1/guilds?guild_id=eq.{guild_config.guild_id}'
        response = requests.patch(url, headers=HEADERS, json=guild_config.to_db(), timeout=10)
        if response.status_code not in [200, 204]:
            print(f"Error updating guild: {response.text}")

    async def delete_channel(self, channel_id: int):
        try:
            response = requests.delete(f'{SUPABASE_URL}/rest/v1/channels?channel_id=eq.{channel_id}', headers=HEADERS, timeout=10)
            response.raise_for_status()
            if channel_id in self.channels:
                del self.channels[channel_id]
        except Exception as e:
            print(f"Error deleting channel {channel_id}: {e}")

    def get_config(self, guild_id: int) -> Optional[GuildConfig]:
        return self.guild_configs.get(guild_id)

    async def register_guild(self, guild_id: int, available_cat: int, used_cat: int, **kwargs):
        config = GuildConfig(guild_id=guild_id, available_category_id=available_cat, used_category_id=used_cat, **kwargs)
        self.guild_configs[guild_id] = config
        self.save_guild(config)

    async def register_channel(self, channel_id: int, guild_id: int):
        if channel_id not in self.channels:
            channel_data = ChannelData(channel_id=channel_id, guild_id=guild_id, state=ChannelState.AVAILABLE.value)
            self.channels[channel_id] = channel_data
            self.save_channel(channel_data)

    async def claim_channel(self, channel: discord.TextChannel, user: discord.User, message_id: int):
        async with self.locks[channel.id]:
            if channel.id not in self.channels:
                return False
            chan_data = self.channels[channel.id]
            if chan_data.state != ChannelState.AVAILABLE.value:
                return False
            config = self.get_config(channel.guild.id)
            if not config:
                return False
            user_channels = sum(1 for c in self.channels.values() if c.owner_id == user.id and c.state in [ChannelState.USED.value, ChannelState.CLAIMED.value])
            if user_channels >= config.max_per_user:
                await channel.send(embed=discord.Embed(description=f"You already have {config.max_per_user} active help channels. Please close one first.", color=0xED4245))
                return False
            now = datetime.utcnow().isoformat()
            chan_data.state = ChannelState.CLAIMED.value
            chan_data.owner_id = user.id
            chan_data.claimed_at = now
            chan_data.last_activity = now
            self.save_channel(chan_data)
            try:
                used_cat = self.client.get_channel(config.used_category_id)
                await channel.edit(category=used_cat, name=f"{channel.name.split('-')[0]}-{user.display_name[:20]}")
                msg = await channel.fetch_message(message_id)
                await msg.pin()
                chan_data.state = ChannelState.USED.value
                self.save_channel(chan_data)
            except discord.Forbidden:
                print(f"Missing permissions to move channel {channel.id}")
            except Exception as e:
                print(f"Error moving channel {channel.id}: {e}")
            return True

    async def update_activity(self, channel_id: int, user_id: int):
        if channel_id not in self.channels:
            return
        chan_data = self.channels[channel_id]
        if chan_data.state == ChannelState.USED.value:
            chan_data.last_activity = datetime.utcnow().isoformat()
            self.save_channel(chan_data)

    async def close_channel(self, channel: discord.TextChannel, reason: str):
        async with self.locks[channel.id]:
            if channel.id not in self.channels:
                return False
            chan_data = self.channels[channel.id]
            if chan_data.state != ChannelState.USED.value:
                return False
            config = self.get_config(channel.guild.id)
            if not config:
                return False
            chan_data.state = ChannelState.CLOSING.value
            chan_data.owner_id = None
            chan_data.claimed_at = None
            chan_data.last_activity = None
            self.save_channel(chan_data)
            try:
                await channel.send(embed=discord.Embed(title="Channel Closed", description=f"{reason}\nThis channel will be available for others soon.", color=0x000000))
            except:
                pass
            try:
                pins = await channel.pins()
                for msg in pins:
                    try:
                        await msg.unpin()
                    except:
                        pass
            except:
                pass
            asyncio.create_task(self._delayed_make_available(channel.id, config.close_timeout))
            return True

    async def _delayed_make_available(self, channel_id: int, delay: int):
        await asyncio.sleep(delay)
        channel = self.client.get_channel(channel_id)
        if isinstance(channel, discord.TextChannel):
            await self.make_available(channel)

    async def make_available(self, channel: discord.TextChannel):
        async with self.locks[channel.id]:
            if channel.id not in self.channels:
                return
            chan_data = self.channels[channel.id]
            config = self.get_config(channel.guild.id)
            if not config:
                return
            chan_data.state = ChannelState.AVAILABLE.value
            chan_data.owner_id = None
            chan_data.prompt_message_id = None
            self.save_channel(chan_data)
            try:
                avail_cat = self.client.get_channel(config.available_category_id)
                base_name = channel.name.split('-')[0]
                await channel.edit(category=avail_cat, name=base_name)
                embed = discord.Embed(
                    title="Available Help Channel!",
                    description=(
                        "Send your question here to claim this channel.\n"
                        "**Remember:**\n"
                        "• Ask your question clearly and concisely\n"
                        "• Use `.close` when you're done\n"
                    ),
                    color=0x7CB342
                )
                msg = await channel.send(embed=embed)
                async with self.locks[channel.id]:
                    if channel.id in self.channels:
                        self.channels[channel.id].prompt_message_id = msg.id
                        self.save_channel(self.channels[channel.id])
            except discord.Forbidden:
                print(f"Missing permissions to move channel {channel.id} to available")
            except Exception as e:
                print(f"Error making channel {channel.id} available: {e}")

    async def check_timeouts(self):
        now = datetime.utcnow()
        for channel_id, chan_data in list(self.channels.items()):
            if chan_data.state != ChannelState.USED.value:
                continue
            if not chan_data.last_activity:
                continue
            channel = self.client.get_channel(channel_id)
            if not channel or not isinstance(channel, discord.TextChannel):
                continue
            config = self.get_config(channel.guild.id)
            if not config:
                continue
            last_activity = datetime.fromisoformat(chan_data.last_activity)
            elapsed = (now - last_activity).total_seconds()
            if elapsed > config.activity_timeout:
                await self.prompt_close(channel)

    async def prompt_close(self, channel: discord.TextChannel):
        chan_data = self.channels.get(channel.id)
        if not chan_data or not chan_data.owner_id:
            return
        embed = discord.Embed(
            description=f"<@{chan_data.owner_id}> Is your question resolved?\nReact with ✅ to close or ❌ to keep open.",
            color=0xFFCC00
        )
        msg = await channel.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        chan_data.prompt_message_id = msg.id
        self.save_channel(chan_data)

    async def start_scheduler(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            try:
                await self.check_timeouts()
            except Exception as e:
                print(f"Error in clopen scheduler: {e}")
            await asyncio.sleep(60)

    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        if not message.guild:
            return
        channel_id = message.channel.id
        if channel_id not in self.channels:
            return
        chan_data = self.channels[channel_id]
        if chan_data.state == ChannelState.AVAILABLE.value:
            if message.content.startswith('.'):
                return
            await self.claim_channel(message.channel, message.author, message.id)
        elif chan_data.state == ChannelState.USED.value:
            await self.update_activity(channel_id, message.author.id)

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user.bot:
            return
        channel_id = reaction.message.channel.id
        if channel_id not in self.channels:
            return
        chan_data = self.channels[channel_id]
        if chan_data.prompt_message_id != reaction.message.id:
            return
        if user.id != chan_data.owner_id:
            return
        if str(reaction.emoji) == "✅":
            await self.close_channel(reaction.message.channel, f"Closed by <@{user.id}>")
        elif str(reaction.emoji) == "❌":
            chan_data.last_activity = datetime.utcnow().isoformat()
            self.save_channel(chan_data)
            try:
                await reaction.message.delete()
            except:
                pass