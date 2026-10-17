
import discord
from Bot.BotComponent.Base.CompBotBase import CompBotBase
from Bot.NewVersionTemp.CompBase2024 import CompBase


class CompTest(CompBase):

    test = True

    def Initial(self) -> bool:
        if not super().Initial():
            return False
        self.allEvent["PreSecondEvent"] = True
        self.allEvent["on_message"] = True
        # self.allEvent["on_ready"] = True
        return True


    async def on_message(self, message: discord.Message) -> None:
        pass
        # print(message.attachments)
        # print(message.stickers)
        # for sticker in message.stickers:
        #     # await sticker.save("test.gif")
        #     # sticker.save("test.gif")
        #     print(sticker.url)
        #     test = await sticker.fetch()
        #     print(type(test))

        #     print(test)
        #     pass
        # print(message.guild.channels)
    
        # await message.channel.send(":p_p:")
        # await message.channel.send("<:p_p:840773289991208970>")
        
        

    async def CallOnce(self):
        print("CallOnce")

        guild = self.botClient.GetGuild()
        for member in guild.members:
            if member.name[0] == 'h':
                print(member.name, " , ", member.id, " , ", member.display_name)

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
            self.LogW("call test")
            await self.CallOnce()
