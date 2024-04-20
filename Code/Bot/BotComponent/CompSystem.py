

import datetime
from Bot.BotComponent.Base.CompBotBase import CompBotBase
from Bot.NewVersionTemp.CompBase2024 import CompBase


class CompSystem(CompBase):
    updateSecond: int = 10
    secondCount: int = 0

    def Initial(self) -> bool:
        if not super().Initial():
            return False

        self.allEvent["PreSecondEvent"] = True
        self.allEvent["on_ready"] = True

        self.updateSecond = 10

        self.CheckKey()
        return True

    async def on_ready(self) -> None:
        kiedveian = await self.botClient.fetch_user(160763041447804938)
        if kiedveian != None:
            await kiedveian.send(f"機器人登入了：{self.botClient.GetGuild()}")
        command = (
            f"SELECT str_value FROM discord_bot.system_data WHERE database_postfix='{self.botSettings.sqlPostfix}'")
        datas = self.sql.SimpleSelect(command)
        seconds = int(datas[0][0])
        duration = datetime.timedelta(seconds=seconds)
        self.LogI(f"上次持續時間{seconds}秒，({duration})")

    def CheckKey(self):
        pass

    def UpdateHeartbeat(self):
        command = (f"UPDATE system_data  SET str_value='{self.secondCount}'"
                   f" WHERE no>0 AND database_postfix='{self.botSettings.sqlPostfix}' AND col_key='Heartbeat'")
        self.sql.SimpleCommand(command)

    async def PreSecondEvent(self):
        self.secondCount += 1
        if self.secondCount % self.updateSecond == 0:
            self.UpdateHeartbeat()
