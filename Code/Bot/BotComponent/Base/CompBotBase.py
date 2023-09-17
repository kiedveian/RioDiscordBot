

from Bot.BotComponent.Base.CompBase import CompBase
from Bot.BotComponent.BotClient import BotClient
from Bot.BotComponent.BotSettings import BotSettings
from Utility.MysqlManager import MysqlManager


class CompBotBase(CompBase):
    sql: MysqlManager
    botClient: BotClient
    botSettings: BotSettings

    def CanInitial(self) -> bool:
        return self.botSettings != None and self.sql != None and self.botClient != None

    def SetComponents(self, bot):
        super().SetComponents(bot)

        self.sql = bot.GetComponent("sql")
        self.botSettings = bot.GetComponent("botSettings")
        self.botClient = bot.GetComponent("botClient")
