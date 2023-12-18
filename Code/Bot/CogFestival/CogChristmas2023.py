

import random
import discord
from discord.commands import SlashCommandGroup

from Bot.Cogs.CogBase import CogBase
from Bot.SlashCommand.CommandsBot import CommandsBot

# 記錄每個人的故事與賜福
# 抽取故事
# 猜某個人(選取森林伺服器的一個人)
# 暱稱冠上祝福，猜中-冠上自己，猜錯-冠上隨機一人
# (選用功能)：有「是否為處罰」欄位-若為真或1，上方猜中與猜錯結果相反

TEST_USER_LIST = [
    824282959572893696,
    160763041447804938,
]


class ChristmasItem:
    id: int
    member: discord.Member
    story: str
    bless: str


class DrawLog:
    item: ChristmasItem
    drawMember: discord.Member
    guessMember: discord.Member


class CogChristmas2023(CogBase):
    allItems = []
    itemState = {}

    # 輔助搜尋
    logMapByDrawId = {}
    itemMapByMemberId = {}

    def __init__(self, bot: CommandsBot):
        super().__init__(bot)

    async def Initial(self) -> bool:
        if not super().Initial():
            return False
        await self.LoadItems()
        await self.LoadLogs()
        self.LoadSearchDatas()

    async def SetItem(self, item: ChristmasItem, rowData):
        account = rowData[1]
        member = await self.GetMemberByAccount(account)
        if member == None:
            self.LogE(f"找不到成員：{account}")
            return
        item.id = int(rowData[0])
        item.member = member
        item.bless = rowData[2]
        item.story = rowData[3]

    async def LoadItems(self):
        command = f"SELECT id, user, bless, story FROM festival_2023_christmas_item_{self.bot.bot.botSettings.sqlPostfix}"
        selectData = self.bot.bot.sql.SimpleSelect(command)
        allItems = []
        itemMapByMemberId = {}
        for rowData in selectData:
            item = ChristmasItem()
            await self.SetItem(item, rowData)
            allItems.append(item)
            itemMapByMemberId[item.member.id] = item

        self.allItems = allItems
        self.itemMapByMemberId = itemMapByMemberId
        self.LogI(f"聖誕節 全部的故事總數:{len(allItems)}")

    async def LoadLogs(self):
        command = f"SELECT user_id, user_name, draw_user_id, draw_user_name, guess_user_id, guess_user_name FROM festival_2023_christmas_log_{self.bot.bot.botSettings.sqlPostfix}"
        selectData = self.bot.bot.sql.SimpleSelect(command)
        logMapByDrawId = {}
        for rowData in selectData:
            # 932817644954980392
            if int(rowData[0]) not in self.itemMapByMemberId:
                self.LogE(f"找不到對應成員id:{rowData[0]}")
                continue
            log = DrawLog()
            log.item = self.itemMapByMemberId[int(rowData[0])]
            log.drawMember = await self.GetMebmerById(int(rowData[2]))
            if rowData[4] == None:
                log.guessMember = None
            else:
                log.guessMember = await self.GetMebmerById(int(rowData[4]))
            logMapByDrawId[log.drawMember.id] = log
        self.logMapByDrawId = logMapByDrawId
        self.LogI(f"聖誕節 已抽過的故事總數:{len(logMapByDrawId)}")

    def LoadSearchDatas(self):
        # guild: discord.Guild = self.bot.bot.GetGuild()
        # guild.get_member_named()

        pass

    async def GetMemberByAccount(self, account: str) -> discord.Member:
        member = self.bot.GetGuild().get_member_named(account)
        if member == None:
            member = await self.bot.GetGuild().get_member_named(id)
        return member

    async def GetMebmerById(self, id: int) -> discord.Member:
        member = self.bot.GetGuild().get_member(id)
        if member == None:
            member = await self.bot.GetGuild().fetch_member(id)
        return member

    def GetRandomItem(self, onlyNever=True, skipUser=None) -> ChristmasItem:
        if len(self.allItems) <= 0:
            self.LogE("資料錯誤")
            return
        index = -1
        if onlyNever:
            size = len(self.allItems) - len(self.itemState)
            shift = random.randrange(size)
            for index in range(len(self.allItems)):
                if self.allItems[index].member in self.itemState:
                    pass
                else:
                    if shift == 0:
                        chooseIndex = index
                        break
                    else:
                        shift += -1
        else:
            chooseIndex = random.randrange(len(self.allItems))
        self.itemState[self.allItems[chooseIndex].member] = True
        return self.allItems[chooseIndex]

    def InsertDrawLog(self, item: ChristmasItem, drawMember: discord.Member):
        member = item.member
        command = (f"INSERT INTO festival_2023_christmas_log_{self.bot.bot.botSettings.sqlPostfix}"
                   "(user_id, user_name, draw_user_id, draw_user_name)"
                   "VALUES (%s, %s, %s, %s);")
        # command = (f"INSERT INTO festival_2023_christmas_log_{self.bot.bot.botSettings.sqlPostfix}"
        #            "(user_id, user_name, draw_user_id, draw_user_name, guess_user_id, guess_user_name)"
        #            "VALUES (%s, %s, %s, %s, %s, %s);")

        self.bot.bot.sql.SimpleCommand(
            command, (member.id, member.name, drawMember.id, drawMember.name))

    def UpdateGuessLog(self, drawMember: discord.Member):
        pass

    def GetNewNick(self, member: discord.Member, item: ChristmasItem) -> str:
        return item.bless + member.display_name

    christmasGroup = SlashCommandGroup("聖誕節2023", "聖誕節的祝福指令")
    # christmasGroup = SlashCommandGroup("測試群組1212", "測試用的群組說明文字")

    @christmasGroup.command(name="抽取故事", description="抽出故事")
    # @christmasGroup.command(name="測試指令01", description="測試指令1的說明")
    async def draw(self, ctx: discord.ApplicationContext):
        commandMember = await self.GetMebmerById(ctx.user.id)
        if commandMember.id not in TEST_USER_LIST:
            self.LogI(
                f"{commandMember.display_name}({commandMember.name}) 使用指令 draw")
            await ctx.respond("非測試人員請勿使用", ephemeral=True)
            return
        if commandMember.id in self.logMapByDrawId:
            msg = "你已經抽過了故事，抽到的故事："
            item = self.logMapByDrawId[commandMember.id]
        else:
            msg = "抽到的故事："
            item = self.GetRandomItem(onlyNever=False)
            self.InsertDrawLog(item=item, drawMember=commandMember)

        await ctx.respond(msg)
        await ctx.respond(f"{item.story}")
        await ctx.respond(f"接下來請使用指令猜測故事的主人")

    @christmasGroup.command(name="猜測", description="故事的主人")
    # @christmasGroup.command(name="測試指令02",description="測試指令2的說明")
    async def guess(self, ctx: discord.ApplicationContext, guess: discord.Member):
        guessMember = guess
        commandMember = await self.GetMebmerById(ctx.user.id)
        if commandMember.id not in TEST_USER_LIST:
            self.LogI(
                f"{commandMember.display_name}({commandMember.name}) 使用指令 guess")
            await ctx.respond("非測試人員請勿使用", ephemeral=True)
            return

        if commandMember.id not in self.logMapByDrawId:
            await ctx.respond("請先抽過故事再猜")
            return

        drawLog: DrawLog = self.logMapByDrawId[commandMember.id]
        item = drawLog.item
        successful = True
        if drawLog.guessMember != None:
            await ctx.respond("已經猜過了喔")
        else:
            self.UpdateGuessLog(guessMember)
            await ctx.respond(f"猜測的人是{guessMember.display_name}({guessMember.name})")
            if item.member != guessMember:
                successful = False
        blessMember = None
        if successful:
            await ctx.respond(f"答對了，獲得祝福")
            blessMember = commandMember
        else:
            await ctx.respond(f"猜錯了，故事的主人是{item.member.display_name}({item.member.name})")
            blessMember = self.allItems[random.randrange(
                len(self.allItems))].member
            await ctx.respond(f"祝福飛往了{blessMember.display_name}({blessMember.name})")

        newNick = self.GetNewNick(blessMember, item)
        if len(newNick) > 32:
            await ctx.respond(f'暱稱太長了！祝福「{item.bless}」飛走了')
        elif blessMember == self.bot.GetGuild().owner:
            await ctx.respond(f'伺服器擁有者不能改名！！！')
        else:
            self.LogI(f"暱稱更新'{blessMember.display_name}' -> '{newNick}'")
            await blessMember.edit(nick=newNick)


def setup(bot):
    bot.add_cog(CogChristmas2023(bot))
