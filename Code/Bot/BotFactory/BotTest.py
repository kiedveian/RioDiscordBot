
import discord

from Bot.BotFactory.BotNerolirain import BotNerolirain
from Bot.BotComponent.CompTest import CompTest
from Bot.Cogs.Festival.ChineseNewYear2024 import CogChineseNewYear2024
from Bot.Cogs.Festival.AprilFoolDay2024 import CogAprilFoolDay2024
from Bot.BotComponent.CompText2Voice import CompText2Voice


class BotTest(BotNerolirain):
    def _AddAllComponents(self):
        super()._AddAllComponents()

        self.AddComponent("compTest", CompTest())
        # self.AddCog("CompIdiom", CompIdiom())

        # self.AddCog("Christmas2023", CogChristmas2023(self))

        # self.AddComponent("compHistory", CompHistory())
        # self.AddCog("ChineseNewYear2024", CogChineseNewYear2024())

        # self.AddCog("AprilFoolDay2024", CogAprilFoolDay2024())

        # self.AddCog("CompText2Voice", CompText2Voice())
        
