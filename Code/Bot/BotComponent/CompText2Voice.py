
import discord

from Bot.NewVersionTemp.CompBase2024 import CompBase

# openai.api_key = API_KEY


class CompText2Voice(CompBase):
    pass

    def Initial(self) -> bool:
        if not super().Initial():
            return False

        self.allEvent["on_message"] = True
        return True

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.botClient.user:
            return

        if message.author.id != 160763041447804938:
            return

        await message.reply(message.content, tts=True)
