

import datetime
import random
import discord
from discord.ext import pages

from Bot.NewVersionTemp.CompBase2024 import CompBase

# 由聖誕節2023複製修改而來，因此原本故事(story)為新的目標(target)
# 記錄每個人的目標與賜福
# 抽取目標
# 猜某個人(選取森林伺服器的一個人)
# 暱稱冠上祝福，猜中-冠上自己，猜錯-冠上隨機一人
# (選用功能)：有「是否為處罰」欄位-若為真或1，上方猜中與猜錯結果相反

HIDE_MEMBER = None

COMMAND_DRAW = "新年-抽取目標"
COMMAND_GUESS = "新年-猜測"


class FestivalItem:
    id: int
    member: discord.Member
    story: str
    bless: str


class DrawLog:
    item: FestivalItem
    drawMember: discord.Member
    guessMember: discord.Member
    blessMember: discord.Member
    drawTime: datetime.datetime


gCogObj = None


class CogChineseNewYear2024(CompBase):
    allItems = []
    cacheBlessMembers = []

    def Initial(self) -> bool:
        global gCogObj
        if not super().Initial():
            return False
        self.allEvent["on_ready"] = True
        gCogObj = self

        return True

    async def on_ready(self) -> None:
        global HIDE_MEMBER
        await self.LoadItems()
        await self.LoadLogs()
        self.LoadBlessMemebers(30)
        HIDE_MEMBER = self.botClient.user

    async def SetItem(self, item: FestivalItem, rowData):
        account = rowData[1]
        if account == None:
            member = HIDE_MEMBER
        else:
            member = await self.GetMemberByAccount(account)
            if member == None:
                self.LogE(f"找不到成員：{account}")
                member = HIDE_MEMBER
        item.id = int(rowData[0])
        item.member = member
        item.bless = rowData[2]
        item.story = rowData[3]

    async def LoadItems(self):
        command = f"SELECT id, user, bless, story FROM festival_2024_chinese_new_year_item_{self.botSettings.sqlPostfix}"
        selectData = self.sql.SimpleSelect(command)
        allItems = []
        itemMapByItemId = {}
        for rowData in selectData:
            item = FestivalItem()
            await self.SetItem(item, rowData)
            allItems.append(item)
            # itemMapByMemberId[item.member.id] = item
            itemMapByItemId[item.id] = item

        self.allItems = allItems
        self.itemMapByItemId = itemMapByItemId
        # self.itemMapByMemberId = itemMapByMemberId
        self.LogI(f"新年 全部的目標總數:{len(allItems)}")

    async def LoadLogs(self):
        command = (f"SELECT item_id, draw_user_id, draw_user_name, draw_time, guess_user_id, guess_user_name, bless_user_id, bless_user_name"
                   f" FROM festival_2024_chinese_new_year_log_{self.botSettings.sqlPostfix}")
        selectData = self.sql.SimpleSelect(command)
        logMapByDrawId = {}
        for rowData in selectData:
            if int(rowData[0]) not in self.itemMapByItemId:
                self.LogE(f"找不到對應item id:{rowData[0]}")
                continue
            log = DrawLog()
            log.item = self.itemMapByItemId[int(rowData[0])]
            log.drawMember = await self.GetMebmerById(int(rowData[1]))
            if log.drawMember == None:
                continue
            log.drawTime = rowData[3]
            log.guessMember = None
            log.blessMember = None
            if rowData[4] != None:
                log.guessMember = await self.GetMebmerById(int(rowData[4]))
                if rowData[6] != None:
                    log.blessMember = await self.GetMebmerById(int(rowData[6]))
            logMapByDrawId[log.drawMember.id] = log
        self.logMapByDrawId = logMapByDrawId
        self.LogI(f"新年 已抽過的目標人數:{len(logMapByDrawId)}")

    def LoadBlessMemebers(self, days=30):
        blessMembers = []
        checkTime = datetime.datetime.now() - datetime.timedelta(days=days)
        timeString = checkTime.strftime("%Y-%m-%d")
        self.LogI(f"抓取日期{timeString}之後的成員")
        command = (f'SELECT member_id FROM discord_bot.message_log_{self.botSettings.sqlPostfix} '
                   f' WHERE create_time >= "{timeString}" AND guild_id = {self.botClient.GetGuild().id} '
                   f' GROUP BY member_id;')
        selectData = self.sql.SimpleSelect(command)
        for rowData in selectData:
            blessMembers.append(rowData[0])
        self.cacheBlessMembers = blessMembers
        self.LogI(f"新年 隨機飛往祝福的成員總數:{len(self.cacheBlessMembers)}")

    async def GetMemberByAccount(self, account: str) -> discord.Member:
        member = self.botClient.GetGuild().get_member_named(account)
        return member

    async def GetMebmerById(self, id: int) -> discord.Member:
        member = self.botClient.GetGuild().get_member(id)
        if member == None:
            try:
                member = await self.botClient.GetGuild().fetch_member(id)
            except discord.NotFound:
                self.LogI(f"找不到id: {id}")
                return None
        return member

    def GetRandomItem(self, onlyNever=True, skipUser=None) -> FestivalItem:
        if len(self.allItems) <= 0:
            self.LogE("資料錯誤")
            return
        chooseIndex = random.randrange(len(self.allItems))
        return self.allItems[chooseIndex]

    async def GetRandomBlessMember(self):
        chooseIndex = random.randrange(len(self.cacheBlessMembers))
        memberId = self.cacheBlessMembers[chooseIndex]
        return await self.GetMebmerById(memberId)

    def InsertDrawLog(self, item: FestivalItem, drawMember: discord.Member):
        log = DrawLog()
        log.item = item
        log.drawMember = drawMember
        log.drawTime = datetime.datetime.now()
        log.guessMember = None
        log.blessMember = None
        timeString = log.drawTime.strftime("%Y-%m-%d %H:%M:%S")
        self.logMapByDrawId[drawMember.id] = log
        command = (f"INSERT INTO festival_2024_chinese_new_year_log_{self.botSettings.sqlPostfix}"
                   "(item_id, draw_user_id, draw_user_name, draw_time)"
                   "VALUES (%s, %s, %s, %s);")
        self.sql.SimpleCommand(
            command, (item.id, drawMember.id, drawMember.name, timeString))

    def UpdateGuessLog(self, log: DrawLog,  guessMember: discord.Member, blessMember: discord.Member):
        command = (f"UPDATE festival_2024_chinese_new_year_log_{self.botSettings.sqlPostfix}"
                   f" SET guess_user_id=%s, guess_user_name=%s, bless_user_id=%s, bless_user_name=%s "
                   f" WHERE item_id = %s")
        log.guessMember = guessMember
        log.blessMember = blessMember
        self.sql.SimpleCommand(
            command, (guessMember.id, guessMember.name, blessMember.id, blessMember.name, log.item.id))

    def GetNewNick(self, member: discord.Member, item: FestivalItem) -> str:
        return item.bless + member.display_name

    async def Respond(self, obj, *args, **kwargs):
        if isinstance(obj, discord.ApplicationContext):
            await obj.respond(*args, **kwargs)
        elif isinstance(obj, discord.interactions.Interaction):
            # await obj.response.send_message(*args, **kwargs)
            await obj.followup.send(*args, **kwargs)

    festivalGroup = discord.SlashCommandGroup("節慶", "節慶相關指令")

    @festivalGroup.command(name=COMMAND_DRAW, description="新年抽出目標")
    async def draw(self, ctx):
        if ctx.channel_id != self.botSettings.festivalChannel:
            await self.Respond(ctx, f"請至<#{self.botSettings.festivalChannel}>下指令", ephemeral=True)
            return
        commandMember = await self.GetMebmerById(ctx.user.id)
        log: DrawLog = None
        msg = None

        ephemeral = False
        if commandMember.id in self.logMapByDrawId:
            log = self.logMapByDrawId[commandMember.id]

        if log != None:
            if log.drawTime != None:
                nextTime = log.drawTime + datetime.timedelta(days=1)
            if log.guessMember == None:
                ephemeral = True
                msg = "你已經抽過了目標且還沒猜測，抽到的目標："
                item = log.item
            elif log.drawTime != None and datetime.datetime.now() < nextTime:
                stamp = int(nextTime.timestamp())
                replyMsg = f"等到 <t:{stamp}:T>(約<t:{stamp}:R>) 才可以抽"
                await self.Respond(ctx, replyMsg)
                return
            else:
                log = None

        if msg == None:
            msg = "抽到的目標："
            item = self.GetRandomItem(onlyNever=False)
            self.InsertDrawLog(item=item, drawMember=commandMember)

        await self.Respond(ctx, f"{msg}{item.story}", ephemeral=ephemeral)
        if log == None or log.guessMember == None:
            await self.Respond(ctx, f"接下來請使用指令猜測目標的主人", ephemeral=ephemeral)

    @festivalGroup.command(name=COMMAND_GUESS, description="猜測目標的主人")
    async def guess(self, ctx: discord.ApplicationContext, guess: discord.Member):
        if ctx.channel_id != self.botSettings.festivalChannel:
            await ctx.respond(f"請至<#{self.botSettings.festivalChannel}>下指令！", ephemeral=True)
            return
        guessMember = guess
        commandMember = await self.GetMebmerById(ctx.user.id)
        if commandMember.id not in self.logMapByDrawId:
            await ctx.respond("請先抽過目標再猜")
            return

        ephemeral = False
        drawLog: DrawLog = self.logMapByDrawId[commandMember.id]
        item = drawLog.item
        successful = True
        neverGuess = drawLog.guessMember == None
        if not neverGuess:
            ephemeral = True
            await ctx.respond(f"已經猜過了喔，猜測的人是{drawLog.guessMember.display_name}({drawLog.guessMember.name})", ephemeral=ephemeral)
            successful = drawLog.guessMember == item.member
        else:
            await ctx.respond(f"猜測的人是{guessMember.display_name}({guessMember.name})", ephemeral=ephemeral)
            if item.member != guessMember:
                successful = False
        blessMemberList = [commandMember]
        flip = False
        if successful ^ flip:
            await ctx.respond(f"答對了，獲得祝福「{item.bless}」", ephemeral=ephemeral)
            blessMemberList = [item.member, commandMember]
        else:
            if item.member == None or item.member == HIDE_MEMBER:
                await ctx.respond(f"猜錯了，目標的主人匿名啦，哈哈", ephemeral=ephemeral)
            else:
                await ctx.respond(f"猜錯了", ephemeral=ephemeral)
            if neverGuess:
                testCount = 0
                member = None
                while testCount < 100 and (member == None or member == commandMember or member == HIDE_MEMBER):
                    testCount += 1
                    member = await self.GetRandomBlessMember()
                if testCount == 100:
                    self.LogW(f"失敗次數過多")
                blessMemberList[0] = member
            else:
                if successful:
                    blessMemberList = [item.member, commandMember]
                else:
                    blessMemberList = [drawLog.blessMember]
            await ctx.respond(f"祝福「{item.bless}」飛往了{blessMemberList[0].display_name}({blessMemberList[0].name})", ephemeral=ephemeral)

        if neverGuess:
            self.UpdateGuessLog(drawLog, guessMember, blessMemberList[0])
            for blessMember in blessMemberList:
                if blessMember == None or blessMember == HIDE_MEMBER:
                    continue
                newNick = self.GetNewNick(blessMember, item)
                if len(newNick) > 32:
                    await ctx.respond(f'暱稱太長了！祝福「{item.bless}」飛走了')
                elif blessMember == self.botClient.GetGuild().owner:
                    await ctx.respond(f'伺服器擁有者不能改名！！！')
                else:
                    self.LogI(
                        f"暱稱更新'{blessMember.display_name}' -> '{newNick}'")
                    await blessMember.edit(nick=newNick)
                    # await ctx.respond(f'測試版本不會更新！！！')
