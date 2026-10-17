

import datetime
from Bot.BotComponent.Base.CompBotBase import CompBotBase


class CompHistory(CompBotBase):
    isRun: bool = False
    finalTimes = {}

    def Initial(self) -> bool:
        if not super().Initial():
            return False

        self.isRun = False
        self.finalTime = datetime.datetime(2000, 1, 1)

        self.allEvent["PreSecondEvent"] = True

    async def PreSecondEvent(self):
        if self.isRun:
            return

        self.isRun = True
        for channel in self.botClient.GetGuild().channels:
            if channel.id != 933025434298372096:
                continue
            print(channel.name)
            afterTime = None
            if channel.id in self.finalTimes:
                afterTime = self.finalTimes[channel.id]
            async for message in channel.history(limit=10, after=afterTime, oldest_first=True):
                print(message.content)

            break
