

import datetime
import re

import discord
from Bot.BotComponent.Base.CompBotBase import CompBotBase


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


class CompUsers(CompBotBase):
    cacheUsers = {}

    def SetComponents(self, bot):
        super().SetComponents(bot)

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
        if userId in self.cacheUsers:
            return self.cacheUsers[userId].ticket
        return 0

    async def ReplayTicket(self, message: discord.Message):
        amount = self.GetTicketCount(message.author.id)
        msg = f"你的機票還有 {amount} 張"
        await message.reply(content=msg)

    async def AddTicket(self, member: discord.Member, amount: int):
        if member.id not in self.cacheUsers:
            # TODO 裡論上不會進到這
            self.LogE("add ticket error state")
            self.LogE(member)
            user = UserData()
            user.id = member.id
            user.account = member.name
            user.ticket = NEW_USER_TICKET_AMOUNT + amount
            self.cacheUsers[member.id] = user

            command = f"INSERT INTO user_data_{self.botSettings.sqlPostfix}(user_id, account, ticket) VALUES (%s, %s, %s)"
            self.sql.SimpleCommand(
                command, (user.id, user.account, user.ticket))
        else:
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
            await self.ReplayTicket(message=message)
