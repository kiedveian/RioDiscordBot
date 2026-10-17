
import discord
from Bot.BotComponent.Base.CompBotBase import CompBotBase
from Bot.NewVersionTemp.CompBase2024 import CompBase


class CompNerolirainTest(CompBase):

    test = True

    def Initial(self) -> bool:
        if not super().Initial():
            return False
        self.allEvent["PreSecondEvent"] = True
        # self.allEvent["on_message"] = True
        # self.allEvent["on_ready"] = True
        return True

    # async def on_message(self, message: discord.Message) -> None:
    #     pass
    #     print(message.attachments)
    #     print(message.guild.channels)

    async def CallOnce(self):

        guild = self.botClient.GetGuild()
        if guild != None:
            # all_channels = await guild.fetch_channels()
            # for channel in all_channels:
            #     print(f"{channel.name} {channel.id}")
            pass
            # rainBotId = 967747322765262848
            # rainBot = await guild.fetch_member(rainBotId)

            # testRoleId = 891347598353518685
            # testRole = guild.get_role(testRoleId)        
            # await rainBot.add_roles(testRole)

        # kiedveian_id = 160763041447804938
        # kiedveian = await self.botClient.fetch_user(kiedveian_id)
        # try:
        #     await kiedveian.send("GNLS")
        # except discord.Forbidden:
        #     channel = self.botClient.GetCloseChannel()
        #     await channel.send(f"私訊 {kiedveian.display_name}({kiedveian.name}) 失敗")

    async def PreSecondEvent(self):
        if self.test:
            self.test = False
            self.LogW("nerolirain test")
            await self.CallOnce()
