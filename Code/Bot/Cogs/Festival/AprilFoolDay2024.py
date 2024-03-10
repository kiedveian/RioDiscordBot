

import datetime
from Bot.NewVersionTemp.CompBase2024 import CompBase
from Bot.Cogs.Festival.FestivalDatas import CogFestivalDatas, FestivalId


# 1.提供一個假的冒險之類的遊戲
# 2.提供判定是否開啟供其他使用
# 2-1.抽卡必中假機票
# 2-2.如果有查機票，要回愚人節快樂
#

class DataId:
    # 是否抽過假的機票，key為抽的id，值為是否抽過
    DRAW_FAKE_TICKET = 1


class CogAprilFoolDay2024(CompBase):
    FESTIVAL_ID = FestivalId.APRIL_FOOL_DAY_2024

    compFestivalDatas: CogFestivalDatas = None

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

        now = datetime.datetime.now()
        year = now.year
        self.startTime = datetime.datetime(year=year, month=4, day=1)
        self.endTime = datetime.datetime(year=year, month=4, day=2)

        if now < self.startTime:
            self.LogI("距離愚人節開始剩下: ", self.startTime - datetime.datetime.now())

        self.TransData(self.compFestivalDatas.GetDatas(self.FESTIVAL_ID))

        return True

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
