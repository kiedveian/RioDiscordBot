

import datetime
import random
import re

import discord
from Bot.BotComponent.Base.CompBotBase import CompBotBase
from Bot.NewVersionTemp.CompBase2024 import CompBase


class IdiomItem():
    id: int = -1
    # name: str
    idiom: str


NICK_SIGN = "的"


class IdiomLog():
    user_id: int
    old_nick: str
    idiom: str
    logTime: datetime.datetime
    nextTime: datetime.datetime


class CompIdiom(CompBase):
    allItems = []
    allLogs = {}
    cooldownDelta: datetime.timedelta = None
    displayDeltaTime: datetime.timedelta = None

    def Initial(self) -> bool:
        if not super().Initial():
            return False

        self.allEvent["on_message"] = True
        self.cooldownDelta = datetime.timedelta(
            seconds=self.botSettings.idiomCooldownSecond)
        self.displayDeltaTime = datetime.timedelta(minutes=2)
        self.LoadItems()
        self.LoadLogs()
        return True

    def SetItem(self, item: IdiomItem, rowData):
        item.idiom = rowData[0]

    def LoadItems(self):
        # 因為 id 用不到所以沒處理
        command = f"SELECT idiom FROM idiom_item_{self.botSettings.sqlPostfix}"
        selectData = self.sql.SimpleSelect(command)
        allItems = []
        for rowData in selectData:
            item = IdiomItem()
            self.SetItem(item, rowData)
            allItems.append(item)

        # TODO lock
        self.allItems = allItems
        self.LogI(f"成語總數:{len(allItems)}")

    def LoadLogs(self):
        tableName = f"idiom_log_{self.botSettings.sqlPostfix}"
        command = (f"SELECT t.user_id, t.old_nick, t.idiom, t.log_time"
                   f" FROM ( SELECT user_id, MAX(log_time) as max_time FROM {tableName} GROUP BY user_id ) as r"
                   f" INNER JOIN {tableName} as t ON t.user_id = r.user_id AND t.log_time = r.max_time ;")
        selectData = self.sql.SimpleSelect(command)
        allLogs = {}
        for rowData in selectData:
            log = IdiomLog()
            log.user_id = rowData[0]
            log.old_nick = rowData[1]
            log.idiom = rowData[2]
            log.logTime = rowData[3]
            log.nextTime = log.logTime + self.cooldownDelta
            allLogs[log.user_id] = log
        # TODO lock
        self.allLogs = allLogs

    def GetRandomItem(self) -> IdiomItem:
        if len(self.allItems) <= 0:
            self.LogE("資料錯誤")
            return
        rand = random.randrange(len(self.allItems))
        return self.allItems[rand]

    async def ApplyIdiom(self, member: discord.Member, item: IdiomItem, message: discord.Message, applyChange=True):
        if member == None or item == None or message == None:
            self.LogE(f"參數錯誤 {member}, {item}, {message}")
            return
        self.LogI(f"抽到的成語 {item.idiom}:{member.display_name}({member.name}) ")
        newNick = self.GetNewNick(member, item)
        if len(newNick) > 32:
            await message.reply(f'你的暱稱太長了！！！', mention_author=False)
        else:
            if applyChange:
                if member.id == message.guild.owner.id:
                    self.LogI("擁有者不能改名")
                else:
                    self.LogI(f"暱稱更新'{member.display_name}' -> '{newNick}'")
                    self.UpdateNickLog(member, item)
                    await member.edit(nick=newNick)
            await message.reply(f'萊傑請示橙雨大師的結果為：{item.idiom}', mention_author=False)

    def UpdateNickLog(self, member: discord.Member, item: IdiomItem):
        log = IdiomLog()
        log.user_id = member.id
        log.old_nick = member.display_name
        log.idiom = item.idiom
        log.logTime = datetime.datetime.now()
        log.nextTime = log.logTime + self.cooldownDelta
        self.allLogs[member.id] = log
        command = (f"INSERT INTO idiom_log_{self.botSettings.sqlPostfix}"
                   "(user_id, old_nick, idiom)"
                   "VALUES (%s, %s, %s);")
        self.sql.SimpleCommand(command, (log.user_id, log.old_nick, log.idiom))

    def GetNewNick(self, member: discord.Member, item: IdiomItem):
        removeIdiom = member.display_name
        if member.id in self.allLogs:
            log = self.allLogs[member.id]
            oldIdiom = log.idiom
            preFix = oldIdiom+NICK_SIGN
            if re.match(preFix, member.display_name):
                removeIdiom = member.display_name[len(preFix):]
        return item.idiom + NICK_SIGN + removeIdiom

    def GetUserAllIdiom(self, userId: int):
        command = (f"SELECT idiom FROM idiom_log_{self.botSettings.sqlPostfix}"
                   f" WHERE user_id = {userId}")

        selectData = self.sql.SimpleSelect(command)
        result = []
        for rowData in selectData:
            result.append(rowData[0])
        return result

    async def on_message(self, message: discord.Message) -> None:
        member = message.author

        if message.channel.id == self.botSettings.drawAdminChannel and member.id in self.botSettings.drawAdminList:
            if re.match("!testidiom", message.content):
                item = self.GetRandomItem()
                await self.ApplyIdiom(member, item, message, False)

        if message.channel.id != self.botSettings.idiomChannel:
            return

        if re.match("橙雨大師請賜福給我", message.content):
            if member.id in self.allLogs and datetime.datetime.now() < self.allLogs[member.id].nextTime:
                nextTime = self.allLogs[member.id].nextTime
                stamp = int(nextTime.timestamp())
                replyMsg = f"等到 <t:{stamp}:T>(約<t:{stamp}:R>) 才可以抽"
                await message.reply(replyMsg, mention_author=False)
                return

            item = self.GetRandomItem()
            await self.ApplyIdiom(member, item, message)

        if re.match("!賜福歷史", message.content):
            datas = self.GetUserAllIdiom(message.author.id)
            if len(datas) == 0:
                await message.reply("沒有賜福記錄", mention_author=False)
            else:
                await message.reply(">".join(datas), mention_author=False)

    async def idiom_history(self, ctx: discord.ApplicationContext, count: int = 10):
        datas = self.GetUserAllIdiom(ctx.author.id)
        if count > 0 and len(datas) > count:
            datas = datas[:count]
        if len(datas) == 0:
            await ctx.respond("沒有賜福記錄")
        else:
            await ctx.respond(">".join(datas))
