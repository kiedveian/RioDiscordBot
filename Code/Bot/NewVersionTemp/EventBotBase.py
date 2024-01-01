

import traceback
import discord

from Bot.NewVersionTemp.BotCommonBase import BotCommonBase

# from Bot.NewVersionTemp.LogBase import LogBase


# 把 discord event 的東西拆出來這部分

class EventBotBase(BotCommonBase):
    isReady: bool

    allOnReadyObj = []
    allPreSecondObj = []
    allOnMessageObj = []
    allOnRawReactionAddObj = []
    allOnMessageDeleteObj = []
    allOnRawMessageDeleteObj = []
    allOnRawMessageEditObj = []

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.isReady = False
        self.allOnReadyObj = []
        self.allPreSecondObj = []
        self.allOnMessageObj = []
        self.allOnRawReactionAddObj = []
        self.allOnMessageDeleteObj = []
        self.allOnRawMessageDeleteObj = []
        self.allOnRawMessageEditObj = []

    def _AddAllComponents(self):
        super()._AddAllComponents()
        self.allComp["botEvent"] = self

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

# ------------------ 下面為 discord 內建事件 ------------------

    async def on_ready(self) -> None:
        self.LogI('目前登入身份:', self.user)
        self.LogI('登入伺服器:', [guild.name for guild in self.guilds])
        for obj in self.allOnReadyObj:
            try:
                await obj.on_ready()
            except Exception:
                self.LogException(traceback.format_exc())
        await self.setup_hook()
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

    async def setup_hook(self) -> None:
        self.my_background_task.start()

    @discord.ext.tasks.loop(seconds=1)
    async def my_background_task(self):
        try:
            for obj in self.allPreSecondObj:
                await obj.PreSecondEvent()
        except Exception:
            self.LogException(traceback.format_exc())

    @my_background_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()
        self.LogI("初始完畢")
