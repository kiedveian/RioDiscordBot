
from discord import option
from discord.ext import commands


from Bot.Cogs.CogBase import CogBase

class CogTest(CogBase):
    pass

    # def __init__(self, bot: commands.Bot):
    #     self.bot = bot

    @commands.command()
    async def foo(self, ctx: commands.Context):
        ctx.respond(f"GNLS", ephemeral=True)
        pass  # hidden -> True




    @commands.slash_command(name="gnls", description="測試用GNLS")
    async def gnls(self, ctx: commands.Context):
        await ctx.respond(f"GNLS", ephemeral=True)

def setup(bot):
    bot.add_cog(CogTest(bot))
