

from Bot.BotFactory.BotBase import BotBase
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

    def _AddSlashCommands(self):
        super()._AddSlashCommands()

        # self.botClient.load_extension(f"Bot.CogFestival.CogChristmas2023")
