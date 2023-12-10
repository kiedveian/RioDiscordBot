import traceback
import discord
from discord import option
from discord.ext import commands

from Utility.ImageTool import AddTextToImage


class AgeImageCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(name="揍人", description="測試用的指令")
    @option("member", discord.Member,  description="想揍的人")
    async def hit(self, ctx: commands.Context, member):
        await ctx.respond(f"{ctx.author.display_name}  揍了 {member.display_name} 一拳")

    @commands.slash_command(name="生氣圖加字", description="氣噗噗圖加字")
    @option("text", str,  description="長輩圖文字")
    async def age_image(self, ctx: commands.Context, text):
        try:
            srcPath = "../Files/test/image/angry.png"
            outputPath = "../Files/test/image/test001.png"
            AddTextToImage(srcPath, text=text, outputPath=outputPath)
            file = discord.File(fp=outputPath, filename='age_image.png')
        except Exception:
            print(traceback.format_exc())
            await ctx.respond("當機了")
            return
        await ctx.respond(file=file)

    @commands.slash_command(name="客製長輩圖", description="客製一個長輩圖")
    @option("image", discord.Attachment,  description="長輩圖背景")
    @option("text", str,  description="長輩圖文字")
    async def custom_age_image(self, ctx: commands.Context, image, text):
        srcPath = "../Files/test/image/test101.png"
        if image:
            await image.save(srcPath)
        else:
            await ctx.respond("沒有檔案")
        try:
            outputPath = "../Files/test/image/test001.png"
            AddTextToImage(srcPath, text=text, outputPath=outputPath)
            file = discord.File(fp=outputPath, filename='age_image.png')
        except Exception:
            print(traceback.format_exc())
            await ctx.respond("當機了")
            return
        await ctx.respond(file=file)


def setup(bot: commands.Bot):
    bot.add_cog(AgeImageCog(bot))
