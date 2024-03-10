

import discord
from discord import option
from Bot.NewVersionTemp.CompBase2024 import CompBase
from Bot.BotComponent.CompIdiom import CompIdiom
from Bot.BotComponent.CompUsers import CompUsers


class SlashCommandManager(CompBase):

    compIdiom: CompIdiom
    compUsers: CompUsers

    def SetComponents(self, bot):
        super().SetComponents(bot)
        self.compIdiom = bot.GetComponent("compIdiom")
        self.compUsers = bot.GetComponent("compUsers")
        return

    cogBaseGroup = discord.SlashCommandGroup("萊傑rain", "萊傑的一般指令")

    @cogBaseGroup.command(name="賜福歷史", description="顯示最近幾個獲得的賜福")
    @option("count", int,  description="顯示數量,0為全部")
    async def idiom_history(self, ctx: discord.ApplicationContext, count: int = 10):
        await self.compIdiom.idiom_history(ctx, count)

    @cogBaseGroup.command(name="查機票數量", description="顯示自己的機票數量，其他人不會看到")
    async def user_tickets_amount(self, ctx: discord.ApplicationContext):
        await self.compUsers.user_tickets_amount(ctx)
