

import datetime
import random
import re

import discord

from Bot.BotComponent.Base.CompBotBase import CompBotBase
from Bot.BotComponent.CompUsers import CompUsers
from Bot.BotComponent.CompClose import CompClose
from Bot.BotComponent.CompClose import CloseType


DRAW_START_TIME = datetime.datetime(2020, 1, 1)
DRAW_END_TIME = datetime.datetime(2300, 1, 1)

DRAW_TICKET_ID = 1
DRAW_BLACK_HOUSE_ID = 47


class DrawItem:

    id: int = -1
    name: str
    weight: int = 1
    message: str
    image: str
    festival: str
    festival_hint: str

    async def Reply(self, message: discord.Message):
        embed = discord.Embed(description=self.message, color=0x5acef5)
        embed.set_image(url=self.image)
        await message.reply(embed=embed, mention_author=False)

    def IsTicket(self):
        return self.id == DRAW_TICKET_ID

    def IsBlockHouse(self):
        return self.id == DRAW_BLACK_HOUSE_ID


class CompDraw(CompBotBase):
    weightSum: int = 0
    allItems = []
    currentItems = []
    disableItems = []
    selectItemString: str = None
    selectAlarmString: str = None
    updateAlarmMessage: str = None
    nextUpdateTime: datetime.datetime = None

    drawAlarmMessages = {}
    compUsers: CompUsers = None
    compClose: CompClose = None

    def SetComponents(self, bot):
        super().SetComponents(bot)
        self.compClose = bot.GetComponent("compClose")
        self.compUsers = bot.GetComponent("compUsers")

    def Initial(self) -> bool:
        if not super().Initial():
            return False

        self.allEvent["on_message"] = True
        self.allEvent["PreSecondEvent"] = True
        self.selectItemString = f"SELECT item_id, name, weight, message, image, festival, festival_hint FROM draw_item_{self.botSettings.sqlPostfix} where weight != 0"
        self.selectAlarmString = f"SELECT user_id, draw_alarm_message FROM user_data_{self.botSettings.sqlPostfix} WHERE draw_alarm_message != 0"
        self.updateAlarmMessage = f"UPDATE user_data_{self.botSettings.sqlPostfix} SET draw_alarm_message = %s WHERE user_id = %s"

        self.LoadItems()
        self.LoadAlarmMessages()

        return True

    def SetItem(self, item: DrawItem, rowData):
        item.id = rowData[0]
        item.name = rowData[1]
        item.weight = rowData[2]
        item.message = rowData[3]
        item.image = rowData[4]
        item.festival = rowData[5]
        item.festival_hint = rowData[6]

    def CreateMonthDuration(self, nowTime: datetime.datetime, diffMonth: int, maxSize: int):
        if diffMonth < 0:
            diffMonth += 12

        startMonth = nowTime.month + diffMonth
        startMonthYear = nowTime.year
        if startMonth > 12:
            startMonth -= 12
            startMonthYear += 1

        endMonth = startMonth + 1
        endMonthYear = startMonthYear
        if endMonth > 12:
            endMonth -= 12
            endMonthYear += 1

        result = []
        for diffYears in range(maxSize):
            result.append([datetime.datetime(year=startMonthYear+diffYears, month=startMonth, day=1),
                          datetime.datetime(year=endMonthYear+diffYears, month=endMonth, day=1)])
        return result

    def ComputeDurning(self, item: DrawItem, nowTime: datetime.datetime, maxSize: int = 10):
        if item.festival == None or len(item.festival) == 0:
            return [[DRAW_START_TIME, DRAW_END_TIME]]
        allNubmers = re.findall('[0-9]+', item.festival)
        if item.festival.find("月份"):
            if len(allNubmers) == 1:
                month = int(allNubmers[0])
                return self.CreateMonthDuration(nowTime, month - nowTime.month, 1)
        self.LogW("無法解析節慶")
        return []

    def LoadItems(self):
        global DRAW_TICKET_ID
        global DRAW_BLACK_HOUSE_ID
        self.nextUpdateTime = DRAW_END_TIME
        command = self.selectItemString
        drawData = self.sql.SimpleSelect(command)
        allItems = []
        currentItems = []
        disableItems = []
        weightSum = 0
        nowTime = datetime.datetime.now()
        for drawRow in drawData:
            item = DrawItem()
            self.SetItem(item, drawRow)
            allItems.append(item)
            disable = True
            if item.weight >= 0:
                durnings = self.ComputeDurning(item, nowTime)
                if len(durnings) > 0:
                    if durnings[0][0] <= nowTime and nowTime <= durnings[0][1]:
                        weightSum += item.weight
                        currentItems.append(item)
                        disable = False
                        if durnings[0][1] < self.nextUpdateTime:
                            self.nextUpdateTime = durnings[0][1]
                    else:
                        if durnings[0][0] < self.nextUpdateTime:
                            self.nextUpdateTime = durnings[0][0]
            if disable:
                disableItems.append(item)

            if item.name == "小黑屋":
                DRAW_BLACK_HOUSE_ID = item.id

            if item.name == "機票":
                DRAW_TICKET_ID = item.id

        # TODO lock
        self.weightSum = weightSum
        self.allItems = allItems
        self.currentItems = currentItems
        self.disableItems = disableItems

        self.LogI(f"機票id:{DRAW_TICKET_ID},小黑屋id:{DRAW_BLACK_HOUSE_ID}")
        self.LogI(f"當期卡池數:{len(currentItems)} 總權重:{weightSum}")
        self.LogI(f"下次更新抽卡池時間:{self.nextUpdateTime}")

    def LoadAlarmMessages(self):
        command = self.selectAlarmString
        userDatas = self.sql.SimpleSelect(command)
        alarmDatas = {}
        for rowData in userDatas:
            alarmDatas[rowData[0]] = rowData[1]
        self.drawAlarmMessages = alarmDatas

    def _SendDbLog(self, item: DrawItem, message: discord.Message):
        self.LogI(f"%s(%s)抽到 {item.name}({item.id})" %
                  (message.author.display_name, message.author.name))

    def GetDrawItem(self, rand=None):
        # TODO lock
        if rand == None:
            rand = random.randrange(self.weightSum)
        for item in self.currentItems:
            rand = rand - item.weight
            if rand < 0:
                return item

        return None

    async def Draw(self, message: discord.Message):
        nowTime = datetime.datetime.now()
        if self.nextUpdateTime < nowTime:
            self.LoadItems()
        if self.weightSum <= 0 or len(self.currentItems) == 0:
            self.LogE("Draw data error")
            return

        item = self.GetDrawItem()
        if item == None:
            self.LogE("CompDraw Draw no find item")
            return
        await self.ProcessItem(message, item)

    async def ProcessItem(self, message: discord.Message, item: DrawItem):
        await item.Reply(message)
        self._SendDbLog(item=item, message=message)
        if item.IsTicket():
            self.compUsers.AddTicket(message.author, 1)
        elif item.IsBlockHouse():
            await self.compClose.CloseByDraw(message)


# ------------------ 下面為管理員身份功能 ------------------


    async def _TryAdminCommand(self, message: discord.Message) -> bool:
        if message.channel.id != self.botSettings.drawAdminChannel:
            return False
        if message.author.id not in self.botSettings.drawAdminList:
            return False
        if re.match("!drawtestcount", message.content):
            await self._DrawCount(message, message.content[15:])
            return True

        if re.match("!drawrate", message.content):
            await self._ReplayDrawRate(message, message.content[10:])
            return True

        if re.match("!drawtestid", message.content):
            await self._DrawTest(message, message.content[12:])
            return True
        return False

    async def _DrawCount(self, message: discord.message, paraMessage):
        sumItem = {}
        count = int(paraMessage)
        for loop in range(count):
            item = self.GetDrawItem()
            if item not in sumItem:
                sumItem[item] = 0
            sumItem[item] += 1

        replyMessage = ""
        for item in sumItem:
            replyMessage += f"{item.name}({item.id}): {sumItem[item]}次, "
        if message != None:
            await message.reply(replyMessage, mention_author=False)

    async def _ReplayDrawRate(self, message: discord.message, paraMessage):
        weightGroup = {}
        for item in self.currentItems:
            if item.weight not in weightGroup:
                weightGroup[item.weight] = []
            weightGroup[item.weight].append(item)

        replyMessage = ""
        for weight in weightGroup:
            rate = round(weight*100.0/self.weightSum, 2)
            string = f"機率為{weight}/{self.weightSum}({rate}%)有{len(weightGroup[weight])}個："
            for item in weightGroup[weight]:
                string += f"{item.name}({item.id}),"
            replyMessage += string + "\n"

        disableString = f"抽不到的有{len(self.disableItems)}個："
        for item in self.disableItems:
            disableString += f"{item.name}({item.id}),"
        replyMessage += disableString + "\n"

        await message.reply(replyMessage, mention_author=False)

    async def _DrawTest(self, message: discord.message, paraMessage: str):
        paras = paraMessage.split(" ")
        itemId = int(paras[0])
        neeedProcess = False
        if len(paras) > 1:
            neeedProcess = bool(paras[1])
        for item in self.allItems:
            if item.id == itemId:
                if neeedProcess:
                    await self.ProcessItem(message, item)
                else:
                    await item.Reply(message)
                return
        await message.reply(f"找不到對應id {itemId}")

# ------------------ 上面為管理員身份功能 ------------------


# ------------------ 下面為各種事件，給 botClient 呼叫的 ------------------

    async def on_message(self, message: discord.Message) -> None:
        if await self._TryAdminCommand(message):
            return

        if message.channel.id != self.botSettings.drawChannel:
            return
        if re.match("!morning", message.content):
            if self.compUsers.CanDraw(message.author.id):
                newTime = datetime.datetime.now() + datetime.timedelta(hours=12)
                self.compUsers.UpdateDrawTime(message.author, newTime)
                if message.author.id in self.botSettings.morningTimeUserList:
                    self.drawAlarmMessages[message.author.id] = message.id
                    self.sql.SimpleCommand(
                        self.updateAlarmMessage, (message.id, message.author.id))
                await self.Draw(message=message)
            else:
                drawTime = self.compUsers.GetDrawTime(message.author.id)
                stamp = int(drawTime.timestamp())
                await message.reply(f"等到 <t:{stamp}:T>(約<t:{stamp}:R>) 才可以抽", mention_author=False)

    async def PreSecondEvent(self):
        alarmList = []
        for user_id in self.drawAlarmMessages:
            if self.compUsers.CanDraw(user_id):
                message = await self.botClient.FetchChannelMessage(self.botSettings.morningChannelId, self.drawAlarmMessages[user_id])
                if message != None:
                    alarmList.append(user_id)
                    await message.reply("可以抽了")
                    self.sql.SimpleCommand(
                        self.updateAlarmMessage, (0, user_id))

        for user_id in alarmList:
            del self.drawAlarmMessages[user_id]


# ------------------ 上面為各種事件，給 botClient 呼叫的 ------------------
