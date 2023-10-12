

import traceback
import discord

from Bot.BotComponent.BotSettings import BotSettings
from Utility.DebugTool import LogToolGeneral
from Utility.DebugTool import Log


class BotClient(discord.Client):
    DEFAULT_LOG_DEPTH = LogToolGeneral.DEFAULT_LOG_DEPTH + 1
    botSettings: BotSettings

    cacheGuild: discord.Guild
    cacheCloseChannel: discord.TextChannel
    # cacheDrawgChannel: discord.TextChannel
    cacheCloseRole: discord.Role

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.botEvent = None

        self.cacheGuild = None
        self.cacheCloseChannel = None
        # self.cacheDrawgChannel = None
        self.cacheCloseRole = None

    def SetComponents(self, bot):
        self.botSettings = bot.GetComponent("botSettings")
        self.botEvent = bot.GetComponent("botEvent")

    def GetGuild(self) -> discord.Guild:
        if self.cacheGuild == None:
            for guild in self.guilds:
                if guild.id == self.botSettings.closeServerId:
                    self.LogI("設定主伺服器: ", guild)
                    self.cacheGuild = guild
                    break
            if self.cacheGuild == None:
                self.LogE("找不到對應主伺服器: ", guild)
        return self.cacheGuild

    def GetChannel(self, channelId) -> (discord.abc.GuildChannel | None):
        guild = self.GetGuild()
        if guild != None:
            return guild.get_channel(channelId)
        return None

    def GetCloseChannel(self) -> discord.TextChannel:
        if self.cacheCloseChannel == None:
            self.cacheCloseChannel = self.GetChannel(
                self.botSettings.closeChannelId)
        return self.cacheCloseChannel

    def GetCloseRole(self) -> discord.Role:
        if self.cacheCloseRole == None:
            guild = self.GetGuild()
            if guild != None:
                self.cacheCloseRole = guild.get_role(
                    self.botSettings.closeRoleId)
        return self.cacheCloseRole

    async def FetchChannelMessage(self, channelId: int, messageId: int):
        channel = self.get_channel(channelId)
        if channel == None:
            return None
        try:
            message = await channel.fetch_message(messageId)
            return message
        except Exception:
            self.LogE(traceback.format_exc())
        return None

    def _GetLogDepth(self, **kwargs):
        depth = BotClient.DEFAULT_LOG_DEPTH
        if "depth" in kwargs:
            depth = kwargs["depth"]
            del kwargs["depth"]
        return depth

    def LogI(self, *args,  **kwargs):
        Log.I(depth=self._GetLogDepth(**kwargs), *args, **kwargs)

    def LogW(self, *args, **kwargs):
        Log.W(depth=self._GetLogDepth(**kwargs), *args, **kwargs)

    def LogE(self, *args, **kwargs):
        Log.E(depth=self._GetLogDepth(**kwargs), *args, **kwargs)

    async def on_ready(self):
        # 當機器人完成啟動時
        await self.botEvent.on_ready()

    async def on_message(self, *args, **kwargs):
        # 當有訊息時
        await self.botEvent.on_message(*args, **kwargs)

    async def on_raw_reaction_add(self, *args, **kwargs):
        await self.botEvent.on_raw_reaction_add(*args, **kwargs)

    async def on_raw_message_delete(self, *args, **kwargs):
        await self.botEvent.on_raw_message_delete(*args, **kwargs)

    async def on_raw_message_edit(self, *args, **kwargs):
        await self.botEvent.on_raw_message_edit(*args, **kwargs)
