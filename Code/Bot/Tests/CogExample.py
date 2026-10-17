
# pip uninstall discord -y
# pip uninstall py-cord -y

# pip install -U discord.py
# pip install discord.py[voice]
# pip install py-cord

# pip install -U discord-py-slash-command
# pip install -U dpy-appcommands

# pip install -U git+https://github.com/Rapptz/discord.py@rewrite#egg=discord.py[voice]

import discord
from discord.ext import commands
from discord import app_commands, option

from Bot.Cogs.CogBase import CogBase

# @app_commands.guild_only()
# class GroupCogBase(app_commands.Group):
# class CogTest(discord.ext.commands.GroupCog, group_name = "test_group"):


# CogMeta

# @commands.group(pass_context=True)

# class MyCog(commands.Cog, command_attrs=dict(hidden=True)):

# @cog_ext.cog_slash(name="test", guild_ids=guild_ids, description="test")

@app_commands.guild_only()
class CogExample(CogBase, group_name="example_group"):
    pass

    # 一般命令(按鈕命令？)

    @commands.command()
    async def foo(self, ctx):
        pass  # hidden -> True

    @commands.command(hidden=False)
    async def bar(self, ctx):
        pass  # hidden -> False

    # 斜線命令

    @commands.slash_command(name="揍人", description="測試用的指令")
    @option("member", discord.Member,  description="想揍的人")
    async def hit(self, ctx: commands.Context, member):
        await ctx.respond(f"{ctx.author.display_name}  揍了 {member.display_name} 一拳")

    @commands.slash_command(name="生氣圖加字", description="氣噗噗圖加字")
    @option("text", str,  description="長輩圖文字")
    async def age_image(self, ctx: commands.Context, text):
        await ctx.respond(text)

    @commands.slash_command(name="客製長輩圖", description="客製一個長輩圖")
    @option("image", discord.Attachment,  description="長輩圖背景")
    # @option("text", str,  description="長輩圖文字")
    async def custom_age_image(self, ctx: commands.Context, image):
        srcPath = "../Files/test/image/test101.png"
        if image:
            await image.save(srcPath)
            file = discord.File(fp=srcPath, filename="test.png")
            await ctx.respond(file=file)
        else:
            await ctx.respond("沒有檔案")

    @commands.slash_command(name="gnls", description="測試用GNLS")
    async def gnls(self, ctx: commands.Context):
        await ctx.respond(f"GNLS", ephemeral=True)


def setup(bot):
    bot.add_cog(CogExample(bot))
