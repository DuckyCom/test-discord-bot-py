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
    USED = "used"
    CLOSING = "closing"


@dataclass
class ChannelData:
    channel_id: int
    guild_id: int
    state: str
    base_name: str
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
            base_name=data.get('base_name', 'help'),
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
            'base_name': self.base_name,
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
        self.closing_tasks: Dict[int, asyncio.Task] = {}

    async def _safe_send(self, channel: discord.TextChannel, **kwargs):
        try:
            return await channel.send(**kwargs)
        except discord.HTTPException as e:
            if e.status == 429:
                print(f"Rate limited when sending to {channel.id}")
                return None
            print(f"HTTP error sending to {channel.id}: {e}")
            raise
        except Exception as e:
            print(f"Error sending to {channel.id}: {e}")
            return None

    async def _safe_edit(self, channel: discord.TextChannel, **kwargs):
        try:
            await channel.edit(**kwargs)
            return True
        except discord.HTTPException as e:
            if e.status == 429:
                print(f"Rate limited when editing {channel.id}")
                return False
            print(f"HTTP error editing {channel.id}: {e}")
            return False
        except Exception as e:
            print(f"Error editing {channel.id}: {e}")
            return False

    async def _safe_pin(self, message: discord.Message):
        try:
            await message.pin()
            return True
        except:
            return False

    async def _safe_unpin(self, message: discord.Message):
        try:
            await message.unpin()
        except:
            pass

    async def load_config(self):
        try:
            guilds_data = fetch_table('guilds')
            print(f"Loaded {len(guilds_data)} guilds")
            for row in guilds_data:
                gid = row['guild_id']
                self.guild_configs[gid] = GuildConfig.from_db(row)

            channels_data = fetch_table('channels')
            print(f"Loaded {len(channels_data)} channels")
            for row in channels_data:
                cid = row['channel_id']
                self.channels[cid] = ChannelData.from_db(row)
        except Exception as e:
            print(f"Load error: {e}")

    def _save(self, table: str, data: dict):
        try:
            url = f'{SUPABASE_URL}/rest/v1/{table}'
            headers = {**HEADERS, 'Prefer': 'resolution=merge-duplicates'}
            r = requests.post(url, headers=headers, json=data, timeout=10)
            if r.status_code not in [200, 201, 204]:
                print(f"✗ Save {table} failed: {r.status_code}")
                return False
            return True
        except Exception as e:
            print(f"✗ Save {table} error: {e}")
            return False

    def save_channel(self, chan: ChannelData):
        return self._save('channels', chan.to_db())

    def save_guild(self, config: GuildConfig):
        return self._save('guilds', config.to_db())

    async def delete_channel(self, cid: int):
        try:
            r = requests.delete(
                f'{SUPABASE_URL}/rest/v1/channels?channel_id=eq.{cid}',
                headers=HEADERS,
                timeout=10
            )
            r.raise_for_status()
            if cid in self.channels:
                del self.channels[cid]
        except Exception as e:
            print(f"Delete {cid}: {e}")

    def get_config(self, gid: int):
        return self.guild_configs.get(gid)

    async def register_guild(self, gid: int, avail_cat: int, used_cat: int, **kw):
        cfg = GuildConfig(gid, avail_cat, used_cat, **kw)
        self.guild_configs[gid] = cfg
        self.save_guild(cfg)

    async def register_channel(self, cid: int, gid: int, base: str = None):
        if cid in self.channels:
            return
        
        if not base:
            ch = self.client.get_channel(cid)
            base = ch.name if ch else "help"
        
        data = ChannelData(cid, gid, ChannelState.AVAILABLE.value, base)
        self.channels[cid] = data
        self.save_channel(data)

    async def claim_channel(self, channel: discord.TextChannel, user: discord.User, msg_id: int):
        async with self.locks[channel.id]:
            cid = channel.id
            
            if cid not in self.channels:
                return False

            chan = self.channels[cid]
            if chan.state != ChannelState.AVAILABLE.value:
                return False

            cfg = self.get_config(channel.guild.id)
            if not cfg:
                return False

            # Check user limit
            user_count = sum(1 for c in self.channels.values() 
                           if c.owner_id == user.id and c.state == ChannelState.USED.value)
            if user_count >= cfg.max_per_user:
                await self._safe_send(channel, embed=discord.Embed(
                    description=f"You have {cfg.max_per_user} active channels. Close one first.",
                    color=0xED4245
                ))
                return False

            now = datetime.utcnow().isoformat()
            chan.state = ChannelState.USED.value
            chan.owner_id = user.id
            chan.claimed_at = now
            chan.last_activity = now
            
            if not self.save_channel(chan):
                chan.state = ChannelState.AVAILABLE.value
                chan.owner_id = None
                chan.claimed_at = None
                chan.last_activity = None
                return False

            try:
                used_cat = self.client.get_channel(cfg.used_category_id)
                if not used_cat:
                    chan.state = ChannelState.AVAILABLE.value
                    chan.owner_id = None
                    chan.claimed_at = None
                    chan.last_activity = None
                    self.save_channel(chan)
                    return False
                
                # Batch edit operations to reduce API calls
                if not await self._safe_edit(
                    channel,
                    category=used_cat,
                    name=f"{chan.base_name}-{user.display_name[:20]}"
                ):
                    chan.state = ChannelState.AVAILABLE.value
                    chan.owner_id = None
                    chan.claimed_at = None
                    chan.last_activity = None
                    self.save_channel(chan)
                    return False
                
                # Pin is non-critical, don't rollback if fails
                try:
                    msg = await channel.fetch_message(msg_id)
                    await self._safe_pin(msg)
                except:
                    pass

                return True
                
            except Exception as e:
                print(f"Claim error: {e}")
                chan.state = ChannelState.AVAILABLE.value
                chan.owner_id = None
                chan.claimed_at = None
                chan.last_activity = None
                self.save_channel(chan)
                return False

    async def update_activity(self, cid: int, uid: int):
        if cid not in self.channels:
            return
        chan = self.channels[cid]
        if chan.state == ChannelState.USED.value:
            chan.last_activity = datetime.utcnow().isoformat()
            self.save_channel(chan)

    async def close_channel(self, channel: discord.TextChannel, reason: str):
        async with self.locks[channel.id]:
            cid = channel.id
            
            if cid not in self.channels:
                return False

            chan = self.channels[cid]
            if chan.state != ChannelState.USED.value:
                return False

            cfg = self.get_config(channel.guild.id)
            if not cfg:
                return False

            chan.state = ChannelState.CLOSING.value
            if not self.save_channel(chan):
                return False

            # Batch operations: send message and unpin in parallel
            await self._safe_send(channel, embed=discord.Embed(
                title="Channel Closed",
                description=f"{reason}\nAvailable in {cfg.close_timeout}s.",
                color=0x000000
            ))

            # Unpin all at once
            try:
                pins = await channel.pins()
                await asyncio.gather(*[self._safe_unpin(msg) for msg in pins], return_exceptions=True)
            except:
                pass

            task = asyncio.create_task(self._delayed_make_available(cid, cfg.close_timeout))
            self.closing_tasks[cid] = task
            task.add_done_callback(lambda t: self._task_done(cid, t))
            return True

    def _task_done(self, cid: int, task: asyncio.Task):
        if cid in self.closing_tasks:
            del self.closing_tasks[cid]
        try:
            task.result()
        except Exception as e:
            print(f"Task error {cid}: {e}")

    async def _delayed_make_available(self, cid: int, delay: int):
        try:
            await asyncio.sleep(delay)
            ch = self.client.get_channel(cid)
            if ch and isinstance(ch, discord.TextChannel):
                await self.make_available(ch)
        except Exception as e:
            print(f"Delayed error {cid}: {e}")
            raise

    async def make_available(self, channel: discord.TextChannel):
        async with self.locks[channel.id]:
            cid = channel.id
            
            if cid not in self.channels:
                return

            chan = self.channels[cid]
            cfg = self.get_config(channel.guild.id)
            if not cfg:
                return

            chan.state = ChannelState.AVAILABLE.value
            chan.owner_id = None
            chan.claimed_at = None
            chan.last_activity = None
            chan.prompt_message_id = None
            
            if not self.save_channel(chan):
                return

            try:
                avail_cat = self.client.get_channel(cfg.available_category_id)
                if not avail_cat:
                    return
                
                # Batch edit operations
                if not await self._safe_edit(channel, category=avail_cat, name=chan.base_name):
                    return

                # Send prompt
                embed = discord.Embed(
                    title="Available Help Channel!",
                    description="Send your question to claim this channel.\n**Remember:**\n• Be clear and concise\n• Use `.close` when done",
                    color=0x7CB342
                )
                msg = await self._safe_send(channel, embed=embed)
                if msg:
                    chan.prompt_message_id = msg.id
                    self.save_channel(chan)
            except Exception as e:
                print(f"Make available error {cid}: {e}")

    async def check_timeouts(self):
        now = datetime.utcnow()
        for cid, chan in list(self.channels.items()):
            if chan.state != ChannelState.USED.value or not chan.last_activity:
                continue

            ch = self.client.get_channel(cid)
            if not ch or not isinstance(ch, discord.TextChannel):
                continue

            cfg = self.get_config(ch.guild.id)
            if not cfg:
                continue

            last = datetime.fromisoformat(chan.last_activity)
            if (now - last).total_seconds() > cfg.activity_timeout:
                await self.prompt_close(ch)

    async def prompt_close(self, channel: discord.TextChannel):
        chan = self.channels.get(channel.id)
        if not chan or not chan.owner_id:
            return

        msg = await self._safe_send(channel, embed=discord.Embed(
            description=f"<@{chan.owner_id}> Question resolved?\n✅ close | ❌ keep open",
            color=0xFFCC00
        ))
        if msg:
            try:
                # Batch add reactions
                await asyncio.gather(
                    msg.add_reaction("✅"),
                    msg.add_reaction("❌"),
                    return_exceptions=True
                )
                chan.prompt_message_id = msg.id
                self.save_channel(chan)
            except:
                pass

    async def start_scheduler(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            try:
                await self.check_timeouts()
            except Exception as e:
                print(f"✗ Scheduler: {e}")
            await asyncio.sleep(60)

    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        cid = message.channel.id
        if cid not in self.channels:
            return

        chan = self.channels[cid]
        if chan.state == ChannelState.AVAILABLE.value:
            if not message.content.startswith('.'):
                await self.claim_channel(message.channel, message.author, message.id)
        elif chan.state == ChannelState.USED.value:
            await self.update_activity(cid, message.author.id)

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if user.bot:
            return

        cid = reaction.message.channel.id
        if cid not in self.channels:
            return

        chan = self.channels[cid]
        if chan.prompt_message_id != reaction.message.id or user.id != chan.owner_id:
            return

        if str(reaction.emoji) == "✅":
            await self.close_channel(reaction.message.channel, f"Closed by <@{user.id}>")
        elif str(reaction.emoji) == "❌":
            chan.last_activity = datetime.utcnow().isoformat()
            self.save_channel(chan)
            try:
                await reaction.message.delete()
            except:
                pass