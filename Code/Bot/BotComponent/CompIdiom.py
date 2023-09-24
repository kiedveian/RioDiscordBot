

import random
import re

import discord
from Bot.BotComponent.Base.CompBotBase import CompBotBase


class IdiomItem():
    id: int = -1
    # name: str
    idiom: str


NICK_SIGN = "的"


class CompIdiom(CompBotBase):
    allItems = []

    def Initial(self) -> bool:
        if not super().Initial():
            return False

        self.allEvent["on_message"] = True
        self.LoadItems()
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

        # # TODO lock
        # self.weightSum = weightSum
        self.allItems = allItems

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
                    self.SendNickLog(member, item)
                    await member.edit(nick=newNick)
            await message.reply(f'萊傑請示成語大師的結果為：{item.idiom}', mention_author=False)

    def SendNickLog(self, member: discord.Member, item: IdiomItem):
        command = (f"INSERT INTO idiom_log_{self.botSettings.sqlPostfix}"
                   "(user_id, old_nick, idiom)"
                   "VALUES (%s, %s, %s);")
        self.sql.SimpleCommand(
            command, (member.id, member.display_name, item.idiom))

    def GetNewNick(self, member: discord.Member, item: IdiomItem):
        command = (f"SELECT idiom FROM idiom_log_{self.botSettings.sqlPostfix} "
                   f"WHERE user_id = %s ORDER BY no DESC LIMIT 1;")
        selectData = self.sql.SimpleSelect(command, member.id)
        removeIdiom = member.display_name
        if len(selectData) > 0:
            oldIdiom = selectData[0][0]
            preFix = oldIdiom+NICK_SIGN
            if re.match(preFix, member.display_name):
                removeIdiom = member.display_name[len(preFix):]
        return item.idiom + NICK_SIGN + removeIdiom

    async def on_message(self, message: discord.Message) -> None:
        if message.channel.id == self.botSettings.drawAdminChannel and message.author.id in self.botSettings.drawAdminList:
            if re.match("!testidiom", message.content):
                item = self.GetRandomItem()
                member = message.author
                await self.ApplyIdiom(member, item, message, False)

        # 932817644954980392 # 機器人1號
        if re.match("!idiom", message.content):
            item = self.GetRandomItem()
            member = message.author

            # 測試處理
            member = await self.botClient.GetGuild().fetch_member(932817644954980392)
            await self.ApplyIdiom(member, item, message)
