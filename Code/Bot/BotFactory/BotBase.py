

import os
import traceback
import discord
from dotenv import load_dotenv
from Bot.BotComponent.BotSettings import BotSettings
from Bot.BotComponent.Base.CompBase import CompBase
from Bot.SlashCommand.CommandsBot import CommandsBot
from Utility.DebugTool import Log, LogToolGeneral
from Utility.MysqlManager import MysqlManager


class BotBase:
    DEFAULT_LOG_DEPTH = LogToolGeneral.DEFAULT_LOG_DEPTH
    isReady = False
    allComp = {}
    allOnReadyObj = []
    allPreSecondObj = []
    allOnMessageObj = []
    allOnRawReactionAddObj = []
    allOnMessageDeleteObj = []
    allOnRawMessageDeleteObj = []
    allOnRawMessageEditObj = []

    # 通用功能
    sql: MysqlManager
    botClient: CommandsBot
    botSettings: BotSettings

    def __init__(self) -> None:
        self.isReady = False
        self.allComp = {}
        self.botSettings = None
        self.sql = None
        self.botClient = None

    def SetData(self, sqlPostfix: str) -> None:
        self._SetBaseUtility(sqlPostfix)
        self._SetAllBaseData()
        self._SetAllComponents()
        self._AddSlashCommands()

    def _SetBaseUtility(self, sqlPostfix):
        self.allComp["botEvent"] = self

        load_dotenv()

        sql = MysqlManager(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user_name=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            schema_name=os.getenv("MYSQL_SCHEMA_NAME")
        )

        self.botSettings = BotSettings(sqlPostfix)
        self.sql = sql
        self.botSettings.LoadSettings(sql)
        self.allComp["sql"] = sql
        self.allComp["botSettings"] = self.botSettings

    def _SetAllBaseData(self):
        # TODO 可能會有相依性的問題
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.reactions = True
        self.botClient = CommandsBot(command_prefix='!', intents=intents)
        self.botClient.SetComponents(self)
        self.allComp["botClient"] = self.botClient

    def _SetAllComponents(self):
        self._AddAllComponents()
        self._SetAllComponentInitial()
        self._SetAllComponentEvnets()

    def _AddSlashCommands(self):
        pass

    def _AddAllComponents(self):
        # 加入需要的組件
        pass

    def _SetAllComponentInitial(self):
        remainComp = []
        for key in self.allComp:
            comp = self.allComp[key]
            if isinstance(comp, CompBase):
                remainComp.append(comp)
        for comp in remainComp:
            comp.SetComponents(self)
        tryCount = 0
        while tryCount < 100 and len(remainComp) != 0:
            tryCount += 1
            nextComp = []
            for comp in remainComp:
                # comp: CompBase = comp
                if comp.CanInitial():
                    comp.Initial()
                    if not comp.IsInitialized():
                        nextComp.append(comp)
                else:
                    nextComp.append(comp)

            remainComp = nextComp
        if len(remainComp) != 0:
            failList = []
            for key in self.allComp:
                if isinstance(self.allComp[key], CompBase):
                    if not self.allComp[key].IsInitialized():
                        failList.append(failList)
            self.LogW("組件未初始化:", failList)

    def _SetAllComponentEvnets(self):
        self.LogI(f"設定全部的組件事件:", [key for key in self.allComp])
        for key in self.allComp:
            comp = self.allComp[key]
            invert_op = getattr(comp, "HasEvent", None)
            if not callable(invert_op):
                continue

            if comp.HasEvent("on_ready"):
                self.allOnReadyObj.append(comp)
            if comp.HasEvent("on_message"):
                self.allOnMessageObj.append(comp)
            if comp.HasEvent("on_raw_reaction_add"):
                self.allOnRawReactionAddObj.append(comp)
            if comp.HasEvent("PreSecondEvent"):
                self.allPreSecondObj.append(comp)
            if comp.HasEvent("on_message_delete"):
                self.allOnMessageDeleteObj.append(comp)
            if comp.HasEvent("on_raw_message_delete"):
                self.allOnRawMessageDeleteObj.append(comp)
            if comp.HasEvent("on_raw_message_edit"):
                self.allOnRawMessageEditObj.append(comp)

    def _GetLogDepth(self, **kwargs):
        depth = BotBase.DEFAULT_LOG_DEPTH
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

    def GetComponent(self, key: str):
        if key in self.allComp:
            return self.allComp[key]
        self.LogW(f"no find component: {key}")
        return None

    def AddComponent(self, key: str, comp: CompBase):
        if key in self.allComp:
            self.LogW(f"{key} 已存在資料: ", self.allComp[key])
        self.allComp[key] = comp

    async def Start(self):
        await self.botClient.start(self.botSettings.botToken)

    async def PreSecondEvent(self):
        for obj in self.allPreSecondObj:
            await obj.PreSecondEvent()

# ------------------ 下面 discord 內建事件，給 botClient 呼叫的 ------------------

    async def on_ready(self) -> None:
        self.LogI('目前登入身份:', self.botClient.user)
        self.LogI('登入伺服器:', [guild.name for guild in self.botClient.guilds])
        for obj in self.allOnReadyObj:
            try:
                await obj.on_ready()
            except Exception:
                self.LogException(traceback.format_exc())
        await self.botClient.setup_hook()
        self.isReady = True

    async def on_message(self, message: discord.Message) -> None:
        if not self.isReady:
            return
        for obj in self.allOnMessageObj:
            try:
                await obj.on_message(message)
            except Exception:
                self.LogException(traceback.format_exc())

    # async def on_reaction_add(reaction, user) -> None:
    #     pass

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if not self.isReady:
            return
        for obj in self.allOnRawReactionAddObj:
            try:
                await obj.on_raw_reaction_add(payload)
            except Exception:
                self.LogException(traceback.format_exc())

    async def on_message_delete(self, message: discord.Message):
        if not self.isReady:
            return
        for obj in self.allOnMessageDeleteObj:
            try:
                await obj.on_message_delete(message)
            except Exception:
                self.LogException(traceback.format_exc())

    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        if not self.isReady:
            return
        for obj in self.allOnRawMessageDeleteObj:
            try:
                await obj.on_raw_message_delete(payload)
            except Exception:
                self.LogException(traceback.format_exc())

    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        if not self.isReady:
            return
        for obj in self.allOnRawMessageEditObj:
            try:
                await obj.on_raw_message_edit(payload)
            except Exception:
                self.LogException(traceback.format_exc())

# ------------------ 上面 discord 內建事件，給 botClient 呼叫的 ------------------
