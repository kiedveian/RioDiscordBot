

import os
import discord
from dotenv import load_dotenv
from Bot.NewVersionTemp.BotClientInterface import BotClient
from Bot.NewVersionTemp.CompManagerBase import CompManagerBase
from Bot.NewVersionTemp.LogBase import LogBase
from Bot.BotComponent.BotSettings import BotSettings
from Utility.MysqlManager import MysqlManager


class BotCommonBase(discord.ext.commands.Bot, LogBase, CompManagerBase, BotClient):
    sql: MysqlManager
    botSettings: BotSettings

    def __init__(self, *args, **kwargs) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.reactions = True
        super().__init__(*args, command_prefix='!', intents=intents, **kwargs)
        self.botSettings = None
        self.sql = None

    def SetData(self, sqlPostfix: str) -> None:
        self._SetBaseUtility(sqlPostfix)
        self._SetAllComponents()

    def _SetAllComponents(self):
        self._AddAllComponents()
        self._SetAllComponentInitial()
        self._SetAllComponentEvnets()

    def _SetBaseUtility(self, sqlPostfix):
        load_dotenv()

        self.sql = MysqlManager(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user_name=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            schema_name=os.getenv("MYSQL_SCHEMA_NAME")
        )

        self.botSettings = BotSettings(sqlPostfix)
        self.botSettings.LoadSettings(self.sql)
        self.AddComponent("sql", self.sql)
        self.AddComponent("botSettings", self.botSettings)
        self.AddComponent("botClient", self)
