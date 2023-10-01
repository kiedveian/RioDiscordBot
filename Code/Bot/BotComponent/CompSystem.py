

from Bot.BotComponent.Base.CompBotBase import CompBotBase


class CompSystem(CompBotBase):
    updateSecond: int = 10
    secondCount:int = 0

    def Initial(self) -> bool:
        if not super().Initial():
            return False

        self.allEvent["PreSecondEvent"] = True

        self.updateSecond = 10

        self.CheckKey()
        return True

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
