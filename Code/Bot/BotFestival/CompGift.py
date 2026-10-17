

import discord
from Code.Bot.BotComponent.Base.CompBotBase import CompBotBase


class CompGift(CompBotBase):

    def Initial(self) -> bool:
        if not super().Initial():
            return False
        self.allEvent["on_message"] = True
        return True

    async def DmUser(self, user: discord.User):
        try:
            await user.send("GNLS")
        except discord.Forbidden:
            # 無權限
            channel = self.botClient.GetCloseChannel()
            await channel.send(f"私訊 {user.display_name}({user.name}) 失敗")

    async def ProcessDm(self, message: discord.Message):
        pass

    async def ProcessInChannel(self, message: discord.Message):
        pass

    async def on_message(self, message: discord.Message) -> None:
        if message.channel.id == 123:
            await self.ProcessInChannel(message)
            return

        if type(message.channel) is discord.DMChannel:
            await self.ProcessDm(message)
            return
