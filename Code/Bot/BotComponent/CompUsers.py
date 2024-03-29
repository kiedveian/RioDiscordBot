

import datetime
import re

import discord
from Bot.BotComponent.Base.CompBotBase import CompBotBase
from Bot.NewVersionTemp.CompBase2024 import CompBase
from Bot.Cogs.Festival.FestivalFunctions import CogFestivalFunctions


class UserData:
    id: int = -1
    account: str = None
    ticket: int = 0
    nextDrawTime: datetime = None

    def CanDraw(self) -> bool:
        if self.nextDrawTime == None:
            return False
        return self.nextDrawTime < datetime.datetime.now()


# 大禮包
NEW_USER_TICKET_AMOUNT = 3


class CompUsers(CompBase):
    cacheUsers = {}

    compFestivalFunctions: CogFestivalFunctions = None

    def SetComponents(self, bot):
        super().SetComponents(bot)
        self.compFestivalFunctions = bot.GetComponent("compFestivalFunctions")

    def Initial(self) -> bool:
        if not super().Initial():
            return False
        self.allEvent["on_message"] = True
        self.LoadDatabase()
        return True

    def LoadDatabase(self):
        command = f"SELECT user_id, account, ticket, next_draw_time FROM user_data_{self.botSettings.sqlPostfix}"
        userDatas = self.sql.SimpleSelect(command)
        allUsers = {}
        for rowData in userDatas:
            user = UserData()
            user.id = rowData[0]
            user.account = rowData[1]
            user.ticket = rowData[2]
            user.nextDrawTime = rowData[3]
            allUsers[user.id] = user

        self.cacheUsers = allUsers

    def GetDrawTime(self, userId):
        if userId in self.cacheUsers:
            return self.cacheUsers[userId].nextDrawTime
        return None

    def CanDraw(self, userId) -> bool:
        if userId in self.cacheUsers:
            return self.cacheUsers[userId].CanDraw()
        return True

    def GetTicketCount(self, userId) -> int:
        if userId == self.botSettings.closeBossId:
            return 666
        if userId in self.cacheUsers:
            return self.cacheUsers[userId].ticket
        return 0

    async def ReplayTicketByMessage(self, message: discord.Message):
        amount = self.GetTicketCount(message.author.id)
        msg = f"你的機票還有 {amount} 張"
        await message.reply(content=msg)

    async def ReplayTicketByConText(self, ctx: discord.ApplicationContext):
        amount = self.GetTicketCount(ctx.author.id)
        msg = f"你的機票還有 {amount} 張"
        await ctx.respond(msg, ephemeral=True)

    def AddTicket(self, member: discord.Member, amount: int):
        if member.id not in self.cacheUsers:
            self.LogE("找不到使用者")
            return
        if member.id == self.botSettings.closeBossId:
            self.LogI("機票無限")
            return
        self.cacheUsers[member.id].ticket += amount
        command = f"UPDATE user_data_{self.botSettings.sqlPostfix} SET ticket = ticket +(%s) WHERE user_id = %s"
        self.sql.SimpleCommand(command, (amount, member.id))

    def UpdateDrawTime(self, member: discord.Member, newTime: datetime):
        if member.id not in self.cacheUsers:
            user = UserData()
            user.id = member.id
            user.account = member.name
            user.ticket = NEW_USER_TICKET_AMOUNT
            user.nextDrawTime = newTime
            self.cacheUsers[member.id] = user
            command = (f"INSERT INTO user_data_{self.botSettings.sqlPostfix}"
                       "(user_id, account, ticket, next_draw_time) VALUES (%s, %s, %s, %s)")
            self.sql.SimpleCommand(
                command, (user.id, user.account, user.ticket, user.nextDrawTime))
            return
        self.cacheUsers[member.id].nextDrawTime = newTime
        command = f"UPDATE user_data_{self.botSettings.sqlPostfix} SET next_draw_time = %s WHERE user_id = %s"
        self.sql.SimpleCommand(command, (newTime, member.id))

    async def on_message(self, message: discord.Message) -> None:
        if re.match("關誰好呢", message.content):
            if self.compFestivalFunctions.IsFoolDay():
                await message.reply(content="指令維修中，請改用 /查機票數量 ")
            else:
                await self.ReplayTicketByMessage(message=message)

    async def user_tickets_amount(self, ctx: discord.ApplicationContext):
        if self.compFestivalFunctions.IsFoolDay() and self.compFestivalFunctions.FoolDayCheckUserTicketEvent(ctx.author.id):
            amount = self.GetTicketCount(ctx.author.id)
            await ctx.respond(f"你的機票還是{amount}張啦，愚人節快樂", ephemeral=True)
        else:
            await self.ReplayTicketByConText(ctx)
