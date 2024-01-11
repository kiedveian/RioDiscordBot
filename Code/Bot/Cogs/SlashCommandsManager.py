

import discord
from Bot.NewVersionTemp.CompBase2024 import CompBase
from Bot.BotComponent.CompIdiom import CompIdiom
from discord import option


class SlashCommandManager(CompBase):

    compIdiom: CompIdiom

    def SetComponents(self, bot):
        super().SetComponents(bot)
        self.compIdiom = bot.GetComponent("compIdiom")
        return

    cogBaseGroup = discord.SlashCommandGroup("萊傑rain", "萊傑的一般指令")

    @cogBaseGroup.command(name="賜福歷史", description="顯示最近幾個獲得的賜福")
    @option("count", int,  description="顯示數量,0為全部")
    async def idiom_history(self, ctx: discord.ApplicationContext, count: int = 10):
        await self.compIdiom.idiom_history(ctx, count)
