

from Bot.BotComponent.BotClient import BotClient
from Bot.BotComponent.BotSettings import BotSettings
from Utility.MysqlManager import MysqlManager
from Utility.DebugTool import Log


class CompBase:
    sql: MysqlManager
    botClient: BotClient
    botSettings: BotSettings

    allEvent = {}

    def __init__(self) -> None:
        self.allEvent = {}

    def SetComponents(self, bot):
        self.sql = bot.GetComponent("sql")
        self.botSettings = bot.GetComponent("botSettings")
        self.botClient = bot.GetComponent("botClient")

    # def LogI(self, *args, **kwargs):
    #     Log.I(*args, **kwargs)

    # def LogW(self, *args, **kwargs):
    #     Log.W(*args, **kwargs)

    # def LogE(self, *args, **kwargs):
    #     Log.E(*args, **kwargs)
