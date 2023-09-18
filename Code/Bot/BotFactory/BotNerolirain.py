

from Bot.BotFactory.BotBase import BotBase
from Bot.BotComponent.CompLog import CompLog
from Bot.BotComponent.CompUsers import CompUsers
from Bot.BotComponent.CompUpdateDatabase import CompUpdateDatabase
from Bot.BotComponent.CompSnipe import CompSnipe
from Bot.BotComponent.CompClose import CompClose
from Bot.BotComponent.CompDraw import CompDraw


class BotNerolirain(BotBase):

    def _AddAllComponents(self):
        super()._AddAllComponents()

        self.AddComponent("compUsers", CompUsers())
        self.AddComponent("compLog", CompLog())
        self.AddComponent("compUpdateDatabase", CompUpdateDatabase())
        self.AddComponent("compSnipe", CompSnipe())
        self.AddComponent("compDraw", CompDraw())
        self.AddComponent("compClose", CompClose())
