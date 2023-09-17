

from Bot.BotFactory.BotBase import BotBase
from Bot.BotComponent.CompLog import CompLog
from Bot.BotComponent.CompUsers import CompUsers
from Bot.BotComponent.CompUpdateDatabase import CompUpdateDatabase


class BotNerolirain(BotBase):

    def _AddAllComponents(self):
        super()._AddAllComponents()

        self.AddComponent("compUsers", CompUsers())
        self.AddComponent("compLog", CompLog())
        self.AddComponent("compUpdateDatabase", CompUpdateDatabase())
