import discord
from discord import option
from discord.ext import commands


class CogRio(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def morning123(self, ctx: commands.Context):
        await ctx.respond("morning")

    # user_command(
        # message_command
    
    # @commands.slash_command()
    # async def tag456(self, ctx: commands.Context, *, member: discord.Member):
    #     await ctx.respond(f"tag {member}", suppress=True)

    # @commands.slash_command(name="猜測", description="猜猜是誰" )
    # async def guess(self, ctx: commands.Context, member: discord.Member):
    #     """ 猜猜是誰
    #     :param member: 猜的人
    #     """
    #     await ctx.respond(f"猜測 {member.display_name}({member.name})")

    @commands.slash_command(name="揍人",description="測試用的指令" )
    @option("member", discord.Member,  description="想揍的人")
    async def hit(self, ctx: commands.Context, member):
        await ctx.respond(f"{ctx.author.display_name}  揍了 {member.display_name} 一拳")
        
    @commands.slash_command(name="製作長輩圖",description="製作一個長輩圖" )
    @option("text", str,  description="長輩圖文字")
    async def age_image(self, ctx: commands.Context, text):
        await ctx.respond(f"{ctx.author.display_name}  揍了 {member.display_name} 一拳")

    @commands.slash_command(name="客製長輩圖",description="製作一個長輩圖" )
    @option("image", discord.Attachment,  description="長輩圖背景")
    @option("text", str,  description="長輩圖文字")
    async def age_image(self, ctx: commands.Context, image, text):
        if image:
            file = await image.to_file()
            await ctx.respond("Here's your file!", file=file)
            # for attachment in ctx.message.attachments:
            # # fp = BytesIO()
            await attachment.save(attachment.filename)
            file=discord.File(fp=image_binary, filename='image.png')

        else:
            await ctx.respond("You didn't give me a file to reply with! :sob:")


    @commands.slash_command()
    async def hide(self, ctx: commands.Context, data):

        await ctx.respond(f"hide 123", suppress=False)

    @commands.slash_command()
    async def hello(self, ctx, *, member: discord.Member = None):
        """Says hello"""
        member = member or ctx.author
        # if self._last_member is None:
        #     await ctx.send(f'Hello {member.name}~')
        # else:
        await ctx.respond(f'Hello {member.name}... This feels familiar.')
        # self._last_member = member


def setup(bot: commands.Bot):
    print(f"setup ")
    bot.add_cog(CogRio(bot))
