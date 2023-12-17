
import discord
from discord import option
# from discord import app_commands
from discord.ext import commands

from Bot.SlashCommand.CommandsBot import CommandsBot
from Utility.DebugTool import Log, LogToolGeneral


class CogBase(commands.Cog):
    DEFAULT_LOG_DEPTH = LogToolGeneral.DEFAULT_LOG_DEPTH + 1
    bot: CommandsBot = None

    def __init__(self, bot: CommandsBot):
        self.bot = bot
        bot.AddCog(self)

    def IsInitialized(self) -> bool:
        return self.isInitailized

    def CanInitial(self) -> bool:
        return True

    def Initial(self) -> bool:
        # 初始化，由於可能會相其他組件
        self.isInitailized = True
        return self.isInitailized

    def _GetLogDepth(self, **kwargs):
        depth = CogBase.DEFAULT_LOG_DEPTH
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

    def LogException(self, *args, **kwargs):
        Log.E(depth=self._GetLogDepth(**kwargs) + 1, *args, **kwargs)
