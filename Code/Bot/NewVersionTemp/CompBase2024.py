

import discord
from Bot.NewVersionTemp.BotClientInterface import BotClient
from Bot.NewVersionTemp.LogBase import LogBase
from Bot.BotComponent.BotSettings import BotSettings
from Utility.MysqlManager import MysqlManager


class CompBase(discord.ext.commands.Cog, LogBase):
    isInitailized: bool = False
    allEvent = {}
    sql: MysqlManager = None
    botClient: BotClient = None
    botSettings: BotSettings = None

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.isInitailized = False
        self.allEvent = {}
        self.sql = None
        self.botClient = None
        self.botSettings = None

    def IsInitialized(self) -> bool:
        return self.isInitailized

    def CanInitial(self) -> bool:
        # 可否初始化，由於可能會相依其他組件，需等其他組件初始化完成後才可以初始化
        return self.botSettings != None and self.sql != None and self.botClient != None

    def Initial(self) -> bool:
        self.isInitailized = True
        return self.isInitailized

    def SetComponents(self, helper):
        self.sql = helper.GetComponent("sql")
        self.botSettings = helper.GetComponent("botSettings")
        self.botClient = helper.GetComponent("botClient")

    def HasEvent(self, key):
        value = (key in self.allEvent) and self.allEvent[key]
        invert_op = getattr(self, key, None)
        func = callable(invert_op)
        if value ^ func:
            if value:
                self.LogW("找不到函式:", key, self)
                print(self.allEvent)
            else:
                self.LogW("定義函式卻未使用:", key, self)
        return value
