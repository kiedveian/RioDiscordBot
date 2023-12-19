

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
    blessMember: discord.Member


class CogChristmas2023(CogBase):
    allItems = []

    # 輔助搜尋
    itemMapByItemId = {}
    logMapByDrawId = {}
    logMapByItemId = {}

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
        itemMapByItemId = {}
        for rowData in selectData:
            item = ChristmasItem()
            await self.SetItem(item, rowData)
            allItems.append(item)
            # itemMapByMemberId[item.member.id] = item
            itemMapByItemId[item.id] = item

        self.allItems = allItems
        self.itemMapByItemId = itemMapByItemId
        # self.itemMapByMemberId = itemMapByMemberId
        self.LogI(f"聖誕節 全部的故事總數:{len(allItems)}")

    async def LoadLogs(self):
        command = (f"SELECT item_id, draw_user_id, draw_user_name, guess_user_id, guess_user_name, bless_user_id, bless_user_name"
                   f" FROM festival_2023_christmas_log_{self.bot.bot.botSettings.sqlPostfix}")
        selectData = self.bot.bot.sql.SimpleSelect(command)
        logMapByDrawId = {}
        logMapByItemId = {}
        for rowData in selectData:
            if int(rowData[0]) not in self.itemMapByItemId:
                self.LogE(f"找不到對應item id:{rowData[0]}")
                continue
            log = DrawLog()
            log.item = self.itemMapByItemId[int(rowData[0])]
            log.drawMember = await self.GetMebmerById(int(rowData[1]))
            log.guessMember = None
            log.blessMember = None
            if rowData[3] != None:
                log.guessMember = await self.GetMebmerById(int(rowData[3]))
                if rowData[5] != None:
                    log.blessMember = await self.GetMebmerById(int(rowData[5]))
            logMapByDrawId[log.drawMember.id] = log
            logMapByItemId[log.item.id] = log
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
        if onlyNever:
            chooseArray = []
            for index in range(len(self.allItems)):
                item = self.allItems[index]
                if item.id not in self.logMapByItemId:
                    # 沒抽過
                    chooseArray.append(index)

            size = len(chooseArray)
            chooseIndex = chooseArray[random.randrange(size)]
        else:
            chooseIndex = random.randrange(len(self.allItems))
        return self.allItems[chooseIndex]

    def InsertDrawLog(self, item: ChristmasItem, drawMember: discord.Member):
        log = DrawLog()
        log.item = item
        log.drawMember = drawMember
        log.guessMember = None
        log.blessMember = None
        self.logMapByDrawId[drawMember.id] = log
        command = (f"INSERT INTO festival_2023_christmas_log_{self.bot.bot.botSettings.sqlPostfix}"
                   "(item_id, draw_user_id, draw_user_name)"
                   "VALUES (%s, %s, %s);")
        self.bot.bot.sql.SimpleCommand(
            command, (item.id, drawMember.id, drawMember.name))

    def UpdateGuessLog(self, log: DrawLog,  guessMember: discord.Member, blessMember: discord.Member):
        command = (f"UPDATE festival_2023_christmas_log_{self.bot.bot.botSettings.sqlPostfix}"
                   f" SET guess_user_id=%s, guess_user_name=%s, bless_user_id=%s, bless_user_name=%s "
                   f" WHERE item_id = %s")
        log.guessMember = guessMember
        log.blessMember = blessMember
        self.bot.bot.sql.SimpleCommand(
            command, (guessMember.id, guessMember.name, blessMember.id, blessMember.name, log.item.id))

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
            item = self.logMapByDrawId[commandMember.id].item
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
        neverGuess = drawLog.guessMember == None
        if not neverGuess:
            await ctx.respond(f"已經猜過了喔，猜測的人是{drawLog.guessMember.display_name}({drawLog.guessMember.name})")
            successful = drawLog.guessMember == item.member
        else:
            await ctx.respond(f"猜測的人是{guessMember.display_name}({guessMember.name})")
            if item.member != guessMember:
                successful = False
        blessMember = commandMember
        flip = False
        if successful ^ flip:
            await ctx.respond(f"答對了，獲得祝福「{item.bless}」")
            blessMember = commandMember
        else:
            await ctx.respond(f"猜錯了，故事的主人是{item.member.display_name}({item.member.name})")
            if neverGuess:
                while blessMember == commandMember:
                    blessMember = self.allItems[random.randrange(
                        len(self.allItems))].member
            else:
                blessMember = drawLog.blessMember
            await ctx.respond(f"祝福「{item.bless}」飛往了{blessMember.display_name}({blessMember.name})")

        if neverGuess:
            self.UpdateGuessLog(drawLog, guessMember, blessMember)
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
