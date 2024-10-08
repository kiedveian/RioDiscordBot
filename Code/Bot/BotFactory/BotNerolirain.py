

# from Bot.BotFactory.BotBase import BotBase
from Bot.NewVersionTemp.BotBase2024 import BotBase

from Bot.BotComponent.CompClose import CompClose
from Bot.BotComponent.CompDraw import CompDraw
from Bot.BotComponent.CompIdiom import CompIdiom
from Bot.BotComponent.CompLog import CompLog
from Bot.BotComponent.CompRandom import CompRandom
from Bot.BotComponent.CompSnipe import CompSnipe
from Bot.BotComponent.CompSystem import CompSystem
from Bot.BotComponent.CompUpdateDatabase import CompUpdateDatabase
from Bot.BotComponent.CompUsers import CompUsers
from Bot.BotComponent.CompCommands import CompCommands
from Bot.Cogs.Festival.ChineseNewYear2024 import CogChineseNewYear2024
from Bot.Cogs.SlashCommandsManager import SlashCommandManager
from Bot.Cogs.Festival.FestivalFunctions import CogFestivalFunctions
from Bot.Cogs.Festival.FestivalDatas import CogFestivalDatas
from Bot.Cogs.Festival.AprilFoolDay2024 import CogAprilFoolDay2024

from Bot.BotComponent.CompNerolirainTest import CompNerolirainTest

class BotNerolirain(BotBase):

    def _AddAllComponents(self):
        super()._AddAllComponents()

        self.AddComponent("compUsers", CompUsers())
        self.AddComponent("compLog", CompLog())
        self.AddComponent("compUpdateDatabase", CompUpdateDatabase())
        self.AddComponent("compSnipe", CompSnipe())
        self.AddComponent("compDraw", CompDraw())
        self.AddComponent("compClose", CompClose())
        self.AddComponent("compSystem", CompSystem())
        self.AddComponent("compIdiom", CompIdiom())
        self.AddComponent("compRandom", CompRandom())
        self.AddComponent("compCommands", CompCommands())

        self.AddCog("SlashCommand", SlashCommandManager())

        self.AddCog("compFestivalDatas", CogFestivalDatas())
        self.AddCog("compFestivalFunctions", CogFestivalFunctions())

        # self.AddComponent("compNerolirainTest", CompNerolirainTest())

        # self.AddCog("ChineseNewYear2024", CogChineseNewYear2024())

        # self.AddCog("AprilFoolDay2024", CogAprilFoolDay2024())


