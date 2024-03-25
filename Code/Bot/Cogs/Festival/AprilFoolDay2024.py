

import datetime
import discord
import random
from Bot.NewVersionTemp.CompBase2024 import CompBase
from Bot.Cogs.Festival.FestivalDatas import CogFestivalDatas, FestivalId


# 1.提供一個假的冒險之類的遊戲
# 2.提供判定是否開啟供其他使用
# 2-1.抽卡必中假機票
# 2-2.如果有查機票，要回愚人節快樂
# 3. 亂給祝福

COMMAND_DRAW = "愚人節-抽取祝福"


class DataId:
    # 是否抽過假的機票，key為抽的id，值為是否抽過
    DRAW_FAKE_TICKET = 1


class DrawNickLog:
    nick: str
    draw_id: int
    target_id: int
    drawTime: datetime.datetime
    nextTime: datetime.datetime


class CogAprilFoolDay2024(CompBase):
    FESTIVAL_ID = FestivalId.APRIL_FOOL_DAY_2024

    compFestivalDatas: CogFestivalDatas = None

    allLogs = {}
    cooldownDelta: datetime.timedelta = None

    startTime = None
    endTime = None

    drawFakeTicketDatas = {}

    def SetComponents(self, bot):
        super().SetComponents(bot)
        self.compFestivalDatas = bot.GetComponent("compFestivalDatas")

    def Initial(self) -> bool:
        if not super().Initial():
            return False

        if not self.compFestivalDatas.Initial():
            return False

        self.allEvent["on_ready"] = True

        now = datetime.datetime.now()
        year = now.year
        self.cooldownDelta = datetime.timedelta(seconds=82800)

        self.startTime = datetime.datetime(year=year, month=4, day=1)
        self.endTime = datetime.datetime(year=year, month=4, day=2)

        if now < self.startTime:
            self.LogI("距離愚人節開始剩下: ", self.startTime - datetime.datetime.now())

        self.TransData(self.compFestivalDatas.GetDatas(self.FESTIVAL_ID))

        return True

    async def on_ready(self) -> None:
        self.LoadNicks()
        self.LoadLogs()
        self.LoadTargetMemebers(30)

    # 轉換從資料庫獲得的資料

    def TransData(self, sourceMap):
        if DataId.DRAW_FAKE_TICKET in sourceMap:
            drawFakeTicketData = sourceMap[DataId.DRAW_FAKE_TICKET]
            for idString in drawFakeTicketData:
                boolString = drawFakeTicketData[idString]
                self.drawFakeTicketDatas[int(idString)] = int(boolString)

    def InFestival(self, time=None):
        if time == None:
            time = datetime.datetime.now()
        return self.startTime < time and time < self.endTime

    def CheckUserTicketEvent(self, userId) -> bool:
        return userId in self.drawFakeTicketDatas and self.drawFakeTicketDatas[userId] != 0

    def UpdateUserDrawTicketEvent(self, userId):
        self.drawFakeTicketDatas[userId] = 1
        self.compFestivalDatas.InsertOrUpdateData(
            self.FESTIVAL_ID, DataId.DRAW_FAKE_TICKET, str(userId), "1")

    # 下面是祝福亂飛相關功能

    festivalFool = discord.SlashCommandGroup("愚人節", "愚人節相關指令")

    @festivalFool.command(name=COMMAND_DRAW, description="愚人節抽取祝福")
    async def draw(self, ctx):
        if ctx.channel_id != self.botSettings.festivalChannel:
            await self.Respond(ctx, f"請至<#{self.botSettings.festivalChannel}>下指令", ephemeral=True)
            return
        commandMember = await self.GetMebmerById(ctx.user.id)

        if commandMember.id in self.allLogs and datetime.datetime.now() < self.allLogs[commandMember.id].nextTime:
            nextTime = self.allLogs[commandMember.id].nextTime
            stamp = int(nextTime.timestamp())
            replyMsg = f"等到 <t:{stamp}:T>(約<t:{stamp}:R>) 才可以抽"
            await self.Respond(ctx, replyMsg, ephemeral=False)
            return

        nick = self.GetRandomItem()
        targetMember = await self.GetRandomTargetMember()
        if targetMember == self.botClient.GetGuild().owner:
            msg = f"抽到的祝福是「{nick}」，但抽到了「{targetMember.display_name}」，伺服器擁有者不能改名！！！"
        elif targetMember.bot:
            msg = f"抽到的祝福是「{nick}」，但抽到了「{targetMember.display_name}」，不要亂改機器人的名子！！！"
        else:
            msg = f"「{nick}」飛往了{targetMember.display_name}({targetMember.name})"
            await self.UpdateMemberNick(nick=nick, targetMember=targetMember)
        self.UpdateNickLog(nick=nick, drawMember=commandMember,
                           targetMember=targetMember)

        await self.Respond(ctx, f"{msg}", ephemeral=False)

    def LoadNicks(self):
        # 因為 id 用不到所以沒處理
        command = f"SELECT nick FROM festival_2024_fool_day_item_{self.botSettings.sqlPostfix}"
        selectData = self.sql.SimpleSelect(command)
        allItems = []
        for rowData in selectData:
            if len(rowData[0]) > 20:
                self.LogW(f"詞「{rowData[0]}」過長")
                continue
            allItems.append(rowData[0])

        self.allItems = allItems
        self.LogI(f"愚人詞總數:{len(allItems)}")

    def LoadLogs(self):
        tableName = f"festival_2024_fool_day_log_{self.botSettings.sqlPostfix}"
        command = (f"SELECT t.draw_user_id, t.nick, t.target_user_name, t.draw_time"
                   f" FROM ( SELECT draw_user_id, MAX(draw_time) as max_time FROM {tableName} GROUP BY draw_user_id ) as r"
                   f" INNER JOIN {tableName} as t ON t.draw_user_id = r.draw_user_id AND t.draw_time = r.max_time ;")

        selectData = self.sql.SimpleSelect(command)
        allLogs = {}
        for rowData in selectData:
            log = DrawNickLog()
            log.nick = rowData[1]
            log.draw_id = rowData[0]
            log.target_id = rowData[2]
            log.drawTime = rowData[3]
            log.nextTime = log.drawTime + self.cooldownDelta
            allLogs[log.draw_id] = log

        self.allLogs = allLogs

    def LoadTargetMemebers(self, days=30):
        targerMembers = []
        checkTime = datetime.datetime.now() - datetime.timedelta(days=days)
        timeString = checkTime.strftime("%Y-%m-%d")
        self.LogI(f"抓取日期{timeString}之後的成員")
        command = (f'SELECT member_id FROM discord_bot.message_log_{self.botSettings.sqlPostfix} '
                   f' WHERE create_time >= "{timeString}" AND guild_id = {self.botClient.GetGuild().id} '
                   f' GROUP BY member_id;')
        selectData = self.sql.SimpleSelect(command)
        for rowData in selectData:
            targerMembers.append(rowData[0])
        self.cacheTargetMembers = targerMembers
        self.LogI(f"愚人節 隨機飛往祝福的成員總數:{len(self.cacheTargetMembers)}")

    async def GetMebmerById(self, id: int) -> discord.Member:
        member = self.botClient.GetGuild().get_member(id)
        if member == None:
            try:
                member = await self.botClient.GetGuild().fetch_member(id)
            except discord.NotFound:
                self.LogI(f"找不到id: {id}")
                return None
        return member

    def GetRandomItem(self) -> str:
        if len(self.allItems) <= 0:
            self.LogE("資料錯誤")
            return
        rand = random.randrange(len(self.allItems))
        return self.allItems[rand]

    async def GetRandomTargetMember(self) -> discord.Member:
        chooseIndex = random.randrange(len(self.cacheTargetMembers))
        memberId = self.cacheTargetMembers[chooseIndex]
        return await self.GetMebmerById(memberId)

    def UpdateNickLog(self, nick: str, drawMember: discord.Member, targetMember: discord.Member):
        log = DrawNickLog()

        log.nick = nick
        log.draw_id = drawMember.id
        log.target_id = targetMember.id
        log.drawTime = datetime.datetime.now()
        log.nextTime = log.drawTime + self.cooldownDelta
        self.allLogs[drawMember.id] = log
        timeString = log.drawTime.strftime("%Y-%m-%d %H:%M:%S")
        command = (f"INSERT INTO festival_2024_fool_day_log_{self.botSettings.sqlPostfix}"
                   "(nick, draw_user_id, draw_user_name, draw_time, target_user_id, target_user_name)"
                   "VALUES (%s, %s, %s, %s, %s, %s);")
        self.sql.SimpleCommand(
            command, (nick, drawMember.id, drawMember.name, timeString, targetMember.id, targetMember.name))

    async def UpdateMemberNick(self, nick: str, targetMember: discord.Member):
        oldNick = targetMember.display_name
        newNick = nick + oldNick
        if len(newNick) > 32:
            newNick = nick + oldNick[len(nick)-32:]
        await targetMember.edit(nick=newNick)

    async def Respond(self, obj, *args, **kwargs):
        if isinstance(obj, discord.ApplicationContext):
            await obj.respond(*args, **kwargs)
        elif isinstance(obj, discord.interactions.Interaction):
            await obj.followup.send(*args, **kwargs)
