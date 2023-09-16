

import discord

from Bot.BotComponent.BotSettings import BotSettings
from Utility.DebugTool import Log


class BotClient(discord.Client):
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
