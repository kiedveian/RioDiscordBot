
from Bot.NewVersionTemp.CompBase2024 import CompBase
from Bot.Cogs.Festival.AprilFoolDay2024 import CogAprilFoolDay2024

# 節慶函式整合，方便存取節慶函式
# 因此會取用到各節慶函式


class CogFestivalFunctions(CompBase):
    pass

    compAprilFoolDay: CogAprilFoolDay2024 = None

    def SetComponents(self, bot):
        super().SetComponents(bot)
        self.compAprilFoolDay = bot.GetComponent("AprilFoolDay2024")

    # 以下為愚人節相關

    def IsFoolDay(self, *args, **kwargs) -> bool:
        if self.compAprilFoolDay == None:
            return False
        return self.compAprilFoolDay.InFestival(*args, **kwargs)

    def FoolDayCheckUserTicketEvent(self, *args, **kwargs) -> bool:
        if self.compAprilFoolDay == None:
            return False
        return self.compAprilFoolDay.CheckUserTicketEvent(*args, **kwargs)

    def FoolDayUpdateUserDrawTicketEvent(self, *args, **kwargs):
        if self.compAprilFoolDay == None:
            return
        return self.compAprilFoolDay.UpdateUserDrawTicketEvent(*args, **kwargs)

    # 以上為愚人節相關
