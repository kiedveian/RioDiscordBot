#Apple.py
from discord.ext import commands
from discord import Interaction, app_commands,Object

class Apple(commands.Cog):
    def __init__(self,bot:commands.Bot):
        self.bot = bot
        
    @app_commands.command(name = "hi", description="說你好")
    async def hi(self,interaction:Interaction):
        await interaction.response.send_message("你好")
        #如果只想要讓打指令的人看到可以加上 ephemeral=True
        await interaction.response.send_message("你好",ephemeral=True)
    
    #interaction 僅有效3秒鐘，且每一個interacion僅能回覆一次
    @app_commands.command(name = "say", description="說話")
    async def say(self,interaction:Interaction):
        await interaction.response.defer() #可將interaction有效時間延長為15分鐘
        await interaction.followup.send_message("你好")


async def setup(bot:commands.Bot):
    #如需指定特定的伺服器擁有此指令的話，需添加guild/guilds參數
    await bot.add_cog(Apple(bot),guild = Object(id = '伺服器ID(數字)'))