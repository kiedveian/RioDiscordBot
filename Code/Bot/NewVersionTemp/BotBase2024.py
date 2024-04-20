
import traceback
import discord

from Bot.NewVersionTemp.EventBotBase import EventBotBase
from Bot.NewVersionTemp.CompBase2024 import CompBase


# 原本 BotBase 跟 BotClient 是分開的，但在 cog 初始化時只會拿到 botClient，
# 為了拿到 BotBase 整個結構會變很奇怪，因此將 BotBase 改為 commands.Bot 的子類
class BotBase(EventBotBase):

    cacheGuild: discord.Guild = None
    cacheCloseChannel: discord.TextChannel = None
    # cacheDrawgChannel: discord.TextChannel
    cacheCloseRole: discord.Role = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.cacheGuild = None
        self.cacheCloseChannel = None
        self.cacheCloseRole = None

    def AddCog(self, key: str, cog: CompBase):
        self.add_cog(cog)
        self.AddComponent(key, cog)

    def GetGuild(self) -> discord.Guild:
        if self.cacheGuild == None:
            for guild in self.guilds:
                if guild.id == self.botSettings.closeServerId:
                    self.LogI("設定主伺服器: ", guild)
                    self.cacheGuild = guild
                    break
            if self.cacheGuild == None:
                self.LogE("找不到對應主伺服器 ", self.botSettings.closeServerId)
        return self.cacheGuild

    def GetChannel(self, channelId) -> (discord.abc.GuildChannel | None):
        guild = self.GetGuild()
        if guild != None:
            return guild.get_channel(channelId)
        return None

    def GetCloseChannel(self, defaultChannel = None) -> discord.TextChannel:
        if self.botSettings.closeChannelId == -1:
            return defaultChannel
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

    def Start(self):
        self.run(self.botSettings.botToken)
