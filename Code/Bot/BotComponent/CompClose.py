

import datetime
import re
import threading
import discord
# from Bot.BotComponent.Base.CompBotBase import CompBotBase
from Bot.NewVersionTemp.CompBase2024 import CompBase
from Bot.BotComponent.CompUsers import CompUsers

CLOSE_REFLECTION_SHIFT = 1000
EMPTY_DURATION = datetime.timedelta()
# SQL_TIME_FORMAT = "%y-%m-%d %H:%M:%S"


class CloseType:
    NOT_CLOSE = 0
    RIOT = 1
    TICKET = 2
    COMMAND = 3
    # RIOT_REFLECTION = 4
    DRAW = 5


class CloseData:
    closeType: int
    # payload: discord.RawReactionActionEvent
    message: discord.message
    totalTimeDatas = {}
    sendStringList = []
    # duration: datetime.datetime
    isReflection: bool
    sameTime: bool
    isReply: bool
    userString: str

    def __init__(self) -> None:
        self.closeType = CloseType.NOT_CLOSE
        self.message = None
        self.totalTimeDatas = {}
        self.sendStringList = []
        self.isReflection = False
        self.sameTime = True
        self.isReply = True
        self.userString = ""


class CompClose(CompBase):
    cacheReleaseTime = {}
    processCount: int = 0

    updateCloseTimeString = ""
    compUsers: CompUsers = None

    def SetComponents(self, bot):
        super().SetComponents(bot)
        self.compUsers = bot.GetComponent("compUsers")
        return

    def CanInitial(self) -> bool:
        return super().CanInitial() and self.compUsers != None and self.compUsers.IsInitialized()

    def Initial(self) -> bool:
        if not super().Initial():
            return False

        self.allEvent["on_message"] = True
        self.allEvent["on_raw_reaction_add"] = True
        self.allEvent["PreSecondEvent"] = True

        self.processCount = 0

        self.updateCloseTimeString = (f"CALL update_close_time_{self.botSettings.sqlPostfix} "
                                      " (%s, %s, %s, %s, %s, %s, %s)")

        self.UpdateReleaseTime()
        return True

    def UpdateReleaseTime(self):
        self.needUpdateReleaseTime = False
        command = f""" SELECT user_id, end_time FROM close_time_{self.botSettings.sqlPostfix} WHERE
            (invincible_time < UTC_TIMESTAMP() AND end_time > UTC_TIMESTAMP())"""
        timeDatas = self.sql.SimpleSelect(command)
        timeMap = {timeRow[0]: timeRow[1] for timeRow in timeDatas}
        self.cacheReleaseTime = timeMap

    async def CheckRelease(self):
        closeRole = self.botClient.GetCloseRole()
        utcNow = datetime.datetime.now()
        for member in closeRole.members:
            release = member.id not in self.cacheReleaseTime
            if not release:
                releaseTime = self.cacheReleaseTime[member.id]
                release = releaseTime < utcNow
            if release:
                await member.remove_roles(closeRole)
                self.LogI(f"釋放 {member.display_name}({member.id})")

    def GetCloseTypeByReatcion(self, payload: discord.RawReactionActionEvent):
        # 在舊訊息加反應，因為要取頻道和訊息，會比較慢
        if payload.user_id == self.botSettings.closeBotId:
            # 機器人反應不做處理
            return CloseType.NOT_CLOSE
        if payload.guild_id != self.botSettings.closeServerId:
            # 反應只會影響關人，如不符合可直接跳過
            return
        if payload.emoji == None:
            return CloseType.NOT_CLOSE

        if payload.emoji.id == self.botSettings.closeTicketId:
            return CloseType.TICKET
        elif payload.emoji.id in self.botSettings.closeReatcionList:
            return CloseType.RIOT
        return CloseType.NOT_CLOSE

    async def CheckRiotSuccessful(self, payload: discord.RawReactionActionEvent, message: discord.Message):
        if message.created_at < self.botSettings.closeIgnoreTime:
            return False
        # if message.id in self.processMessage:
        #     return False
        for reaction in message.reactions:
            if reaction.emoji != payload.emoji:
                continue
            if reaction.count < self.botSettings.closeReatcionCount:
                continue
            successful = True
            async for user in reaction.users():
                # avoid close again
                if user == self.botClient.user:
                    successful = False
                    break
            if successful:
                return True
        return False

    def GetCloseTimeByCommand(self, message: discord.Message):
        if message.author.id != self.botSettings.closeBossId:
            return None

        transString = message.content
        findData = re.match(self.botSettings.closeKeyString, transString)
        if findData == None:
            return None
        transString = message.content[len(findData.group(0)):]
        users = message.mentions
        roles = message.role_mentions
        for user in users:
            transString = transString.replace("<@%s>" % (user.id), "")
        for role in roles:
            transString = transString.replace("<@&%s>" % (role.id), "")
        transString = transString.replace(" ", "")

        weeks = 0
        days = 0
        hours = 0
        minutes = 0
        seconds = 0
        subString = re.findall("\d+[wdhms]", transString)
        for data in subString:
            match data[-1]:
                # case 'w':
                #     weeks += int(data[:-1])
                case 'd':
                    days += int(data[:-1])
                case 'h':
                    hours += int(data[:-1])
                case 'm':
                    minutes += int(data[:-1])
                case 's':
                    seconds += int(data[:-1])

        duration = datetime.timedelta(
            weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)
        return duration

    def CheckIsReflection(self, author: discord.ClientUser):
        if author == None:
            return False
        return author == self.botClient.user or author.id in self.botSettings.closeAvoidHintUserList

    def _UpdateTotalTime(self, totalTimeDatas, delta: datetime.timedelta, member):
        if member == self.botClient.user:
            self.LogI(f"關人跳過機器人 {member.id}")
            return
        if member.id in self.botSettings.closeAvoidHintUserList:
            self.LogI(f"關人跳過使用者 {member.id}")
            return
        elif member not in totalTimeDatas:
            totalTimeDatas[member] = delta
        else:
            totalTimeDatas[member] = totalTimeDatas[member] + delta

    def GetMemberTotalTime(self, delta: datetime.timedelta, users=[], roles=[]):
        totalTimeDatas = {}
        if delta == EMPTY_DURATION:
            return totalTimeDatas
        for member in users:
            self._UpdateTotalTime(totalTimeDatas, delta, member)
        for role in roles:
            for member in role.members:
                self._UpdateTotalTime(totalTimeDatas, delta, member)
        return totalTimeDatas

    def GetSendStringList(self, closeData: CloseData):
        if len(closeData.totalTimeDatas) == 0:
            self.LogI(closeData.closeType)
            self.LogI(closeData.message)
            return ["當機了！！！"]
        sendList = []
        if closeData.isReflection:
            sendList.append(f"{closeData.userString}不可以亂關！！！")
        elif closeData.closeType == CloseType.TICKET:
            sendList.append(f"{closeData.userString}使用了機票把你關進小黑屋")
        if not closeData.isReply:
            message = closeData.message
            guild_id = message.channel.guild.id
            channel_id = message.channel.id
            message_id = message.id
            sendList.append(
                f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}")
        if len(sendList) == 0:
            sendList.append(None)
        closeRole = self.botClient.GetCloseRole()
        sendList.append(f"Added {closeRole.name} ")
        combineString = len(closeData.totalTimeDatas) == 1
        for member in closeData.totalTimeDatas:
            delta = closeData.totalTimeDatas[member]
            timestamp = int(self.cacheReleaseTime[member.id].timestamp())
            userString = f"{member.display_name}({member.name})"
            currentStr = (f"({delta}) to {userString}"
                          f"，預計釋放時間:<t:{timestamp}:R>")
            if combineString:
                sendList[-1] += currentStr
            else:
                sendList.append(currentStr)
        return sendList

    async def CloseEvent(self, closeData: CloseData):
        closeRole = self.botClient.GetCloseRole()
        nowTime = datetime.datetime.now()
        roleIds = [member.id for member in closeRole.members]
        sqlUpdateValues = []
        self.processCount += 1
        isReflectionInt = 0
        if closeData.isReflection:
            isReflectionInt = 1
        for member in closeData.totalTimeDatas:
            deltaTime = closeData.totalTimeDatas[member]
            if member.id in roleIds:
                self.LogI(f"笨蛋加時間 {member} {deltaTime}")
                if member.id not in self.cacheReleaseTime:
                    self.cacheReleaseTime[member.id] = nowTime
                self.cacheReleaseTime[member.id] += deltaTime
                endTime = self.cacheReleaseTime[member.id]
            else:
                await member.add_roles(closeRole)
                self.LogI(f"笨蛋關時間 {member} {deltaTime}")
                endTime = nowTime + deltaTime
                self.cacheReleaseTime[member.id] = endTime
            totalSeconds = int(deltaTime.total_seconds())
            sqlUpdateValues.append(
                [member.id, nowTime, endTime, member.display_name, closeData.closeType, totalSeconds, isReflectionInt])
        self.processCount += -1
        self.sql.SimpleCommandMany(self.updateCloseTimeString, sqlUpdateValues)

        replyList = self.GetSendStringList(closeData)
        closeData.sendStringList = replyList
        title = replyList[0]

        embed = discord.Embed(color=0x00ff00, title=title)
        for string in replyList[1:]:
            embed.add_field(name="", value=string, inline=False)
        if closeData.isReply:
            await closeData.message.reply(embed=embed, mention_author=False)
        else:
            await self.botClient.GetCloseChannel().send(embed=embed)

# ------------------ 下面為各種事件，給 botClient 呼叫的 ------------------

    async def PreSecondEvent(self):
        if self.processCount > 0:
            self.LogI(f"processCount: {self.processCount}")
            return
        await self.CheckRelease()

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        closeType = self.GetCloseTypeByReatcion(payload)
        if closeType == CloseType.NOT_CLOSE:
            return
        message = await self.botClient.FetchChannelMessage(payload.channel_id, payload.message_id)
        if message == None:
            self.LogW(
                f"empty message, id: {payload.message_id}({payload.channel_id})")
            return
        isReflection = self.CheckIsReflection(message.author)
        if closeType == CloseType.RIOT:
            if not await self.CheckRiotSuccessful(payload, message):
                return

        userString = ""
        if closeType == CloseType.TICKET:
            userString = f"{payload.member.display_name}({payload.member.name})"
            if self.compUsers.GetTicketCount(payload.member.id) <= 0:
                replyMsg = f"<@{payload.member.id}>({payload.member.name}) 沒有機票還想關人啊"
                await message.channel.send(replyMsg)
                return
            self.compUsers.AddTicket(payload.member, -1)

        duration = datetime.timedelta(minutes=3)
        totalTimeDatas = {}
        if isReflection:
            for reation in message.reactions:
                if reation.emoji == payload.emoji:
                    totalTimeDatas = self.GetMemberTotalTime(
                        duration, users=[user async for user in reation.users()])
                    break
        else:
            totalTimeDatas = self.GetMemberTotalTime(
                duration, users=[message.author])
        if closeType == CloseType.RIOT:
            await message.add_reaction(payload.emoji)
        closeData = CloseData()
        closeData.closeType = closeType
        closeData.message = message
        closeData.isReflection = isReflection
        closeData.totalTimeDatas = totalTimeDatas
        closeData.userString = userString
        closeData.isReply = closeType != CloseType.RIOT
        await self.CloseEvent(closeData)

    async def on_message(self, message: discord.Message) -> None:
        duration = self.GetCloseTimeByCommand(message)
        if duration == None or duration == EMPTY_DURATION:
            # 非關人訊息或時間有誤
            return
        totalTimeDatas = self.GetMemberTotalTime(
            duration, users=message.mentions, roles=message.role_mentions)
        closeData = CloseData()
        closeData.closeType = CloseType.COMMAND
        closeData.message = message
        closeData.totalTimeDatas = totalTimeDatas
        closeData.isReply = True
        await self.CloseEvent(closeData)


# ------------------ 上面為各種事件，給 botClient 呼叫的 ------------------

    async def CloseByDraw(self, message: discord.Message):
        duration = datetime.timedelta(minutes=3)
        totalTimeDatas = self.GetMemberTotalTime(
            duration, users=[message.author])
        closeData = CloseData()
        closeData.closeType = CloseType.DRAW
        closeData.message = message
        closeData.isReflection = False
        closeData.totalTimeDatas = totalTimeDatas
        await self.CloseEvent(closeData)
