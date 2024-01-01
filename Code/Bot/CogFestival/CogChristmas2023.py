

import random
import discord
from discord.commands import SlashCommandGroup

# from Bot.Cogs.CogBase import CogBase
from Bot.NewVersionTemp.CompBase2024 import CompBase
from Bot.SlashCommand.CommandsBot import CommandsBot

# 記錄每個人的故事與賜福
# 抽取故事
# 猜某個人(選取森林伺服器的一個人)
# 暱稱冠上祝福，猜中-冠上自己，猜錯-冠上隨機一人
# (選用功能)：有「是否為處罰」欄位-若為真或1，上方猜中與猜錯結果相反

HIDE_MEMBER = None


class ChristmasItem:
    id: int
    member: discord.Member
    story: str
    bless: str
    images: list


class DrawLog:
    item: ChristmasItem
    drawMember: discord.Member
    guessMember: discord.Member
    blessMember: discord.Member


class CogChristmas2023(CompBase):
    allItems = []

    # 輔助搜尋
    itemMapByItemId = {}
    logMapByDrawId = {}

    def Initial(self) -> bool:
        if not super().Initial():
            return False
        self.allEvent["on_ready"] = True
        return True

    async def on_ready(self) -> None:
        global HIDE_MEMBER
        await self.LoadItems()
        await self.LoadLogs()
        self.LoadSearchDatas()
        HIDE_MEMBER = self.botClient.user

    async def SetItem(self, item: ChristmasItem, rowData):
        account = rowData[1]
        if account == None:
            member = HIDE_MEMBER
        else:
            member = await self.GetMemberByAccount(account)
            if member == None:
                self.LogE(f"找不到成員：{account}")
                return
        item.id = int(rowData[0])
        item.member = member
        item.bless = rowData[2]
        item.story = rowData[3]
        item.images = [rowData[4], rowData[5], rowData[6]]
        while item.images[-1] == None:
            item.images.pop()

    async def LoadItems(self):
        command = f"SELECT id, user, bless, story, image1, image2, image3 FROM festival_2023_christmas_item_{self.botSettings.sqlPostfix}"
        selectData = self.sql.SimpleSelect(command)
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
                   f" FROM festival_2023_christmas_log_{self.botSettings.sqlPostfix}")
        selectData = self.sql.SimpleSelect(command)
        logMapByDrawId = {}
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
        self.logMapByDrawId = logMapByDrawId
        self.LogI(f"聖誕節 已抽過的故事人數:{len(logMapByDrawId)}")

    def LoadSearchDatas(self):
        # guild: discord.Guild = self.botClient.GetGuild()
        # guild.get_member_named()

        pass

    async def GetMemberByAccount(self, account: str) -> discord.Member:
        member = self.botClient.GetGuild().get_member_named(account)
        if member == None:
            member = await self.botClient.GetGuild().get_member_named(id)
        return member

    async def GetMebmerById(self, id: int) -> discord.Member:
        member = self.botClient.GetGuild().get_member(id)
        if member == None:
            member = await self.botClient.GetGuild().fetch_member(id)
        return member

    def GetRandomItem(self, onlyNever=True, skipUser=None) -> ChristmasItem:
        if len(self.allItems) <= 0:
            self.LogE("資料錯誤")
            return
        chooseIndex = random.randrange(len(self.allItems))
        return self.allItems[chooseIndex]

    def InsertDrawLog(self, item: ChristmasItem, drawMember: discord.Member):
        log = DrawLog()
        log.item = item
        log.drawMember = drawMember
        log.guessMember = None
        log.blessMember = None
        self.logMapByDrawId[drawMember.id] = log
        command = (f"INSERT INTO festival_2023_christmas_log_{self.botSettings.sqlPostfix}"
                   "(item_id, draw_user_id, draw_user_name)"
                   "VALUES (%s, %s, %s);")
        self.sql.SimpleCommand(
            command, (item.id, drawMember.id, drawMember.name))

    def UpdateGuessLog(self, log: DrawLog,  guessMember: discord.Member, blessMember: discord.Member):
        command = (f"UPDATE festival_2023_christmas_log_{self.botSettings.sqlPostfix}"
                   f" SET guess_user_id=%s, guess_user_name=%s, bless_user_id=%s, bless_user_name=%s "
                   f" WHERE item_id = %s")
        log.guessMember = guessMember
        log.blessMember = blessMember
        self.sql.SimpleCommand(
            command, (guessMember.id, guessMember.name, blessMember.id, blessMember.name, log.item.id))

    def GetNewNick(self, member: discord.Member, item: ChristmasItem) -> str:
        return item.bless + member.display_name

    christmasGroup = SlashCommandGroup("聖誕節", "聖誕節的祝福指令")

    @christmasGroup.command(name="抽取故事", description="抽出故事")
    async def draw(self, ctx: discord.ApplicationContext):
        if ctx.channel_id != self.botSettings.festivalChannel:
            await ctx.respond(f"請至<#{self.botSettings.festivalChannel}>下指令", ephemeral=True)
            return
        commandMember = await self.GetMebmerById(ctx.user.id)
        log = None
        if commandMember.id in self.logMapByDrawId:
            msg = "你已經抽過了故事，抽到的故事："
            log = self.logMapByDrawId[commandMember.id]
            item = log.item
        else:
            msg = "抽到的故事："
            item = self.GetRandomItem(onlyNever=False)
            self.InsertDrawLog(item=item, drawMember=commandMember)

        embeds = []
        page = 0
        for image in item.images:
            if image == None:
                continue
            page += 1
            if page == 1:
                embed = discord.Embed(title=msg)
            else:
                embed = discord.Embed(
                    title=f"({page}/{len(item.images)})")
            embed.set_image(url=image)
            embeds.append(embed)
        await ctx.respond(embeds=embeds)

        # await ctx.respond(f"{item.story}")
        if log == None or log.guessMember == None:
            await ctx.respond(f"接下來請使用指令猜測故事的主人")

    @christmasGroup.command(name="猜測", description="故事的主人")
    async def guess(self, ctx: discord.ApplicationContext, guess: discord.Member):
        if ctx.channel_id != self.botSettings.festivalChannel:
            await ctx.respond(f"請至<#{self.botSettings.festivalChannel}>下指令！", ephemeral=True)
            return
        guessMember = guess
        commandMember = await self.GetMebmerById(ctx.user.id)
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
        blessMemberList = [commandMember]
        flip = False
        if successful ^ flip:
            await ctx.respond(f"答對了，獲得祝福「{item.bless}」")
            blessMemberList = [item.member, commandMember]
        else:
            if item.member == None or item.member == HIDE_MEMBER:
                await ctx.respond(f"猜錯了，故事的主人匿名啦，哈哈")
            else:
                await ctx.respond(f"猜錯了")
            if neverGuess:
                testCount = 0
                while testCount < 100 and (blessMemberList[0] == commandMember or blessMemberList[0] == HIDE_MEMBER):
                    testCount += 1
                    blessMemberList[0] = self.allItems[random.randrange(
                        len(self.allItems))].member
                if testCount == 100:
                    self.LogW(
                        f"失敗次數過多 {blessMemberList[0].display_name}({blessMemberList[0].name})")
            else:
                if successful:
                    blessMemberList = [item.member, commandMember]
                else:
                    blessMemberList = [drawLog.blessMember]
            await ctx.respond(f"祝福「{item.bless}」飛往了{blessMemberList[0].display_name}({blessMemberList[0].name})")

        if neverGuess:
            self.UpdateGuessLog(drawLog, guessMember, blessMemberList[0])
            for blessMember in blessMemberList:
                if blessMember == None or blessMember == HIDE_MEMBER:
                    continue
                newNick = self.GetNewNick(blessMember, item)
                if len(newNick) > 32:
                    await ctx.respond(f'暱稱太長了！祝福「{item.bless}」飛走了')
                elif blessMember == self.bot.GetGuild().owner:
                    await ctx.respond(f'伺服器擁有者不能改名！！！')
                else:
                    self.LogI(
                        f"暱稱更新'{blessMember.display_name}' -> '{newNick}'")
                    await blessMember.edit(nick=newNick)
                    # await ctx.respond(f'測試版本不會更新！！！')


def setup(bot):
    bot.AddCog("Christmas2023", CogChristmas2023(bot))
    # cog = CogChristmas2023(bot)
    # bot.AddComponent("Christmas2023", cog)

    # bot.add_cog(CogChristmas2023(bot))
