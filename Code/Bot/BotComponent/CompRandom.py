

import random
import re

import discord
from Bot.BotComponent.Base.CompBotBase import CompBotBase
from Bot.NewVersionTemp.CompBase2024 import CompBase


class CompRandom(CompBase):
    commandKey = "!隨機"

    def Initial(self) -> bool:
        if not super().Initial():
            return False

        self.allEvent["on_message"] = True

        return True

    async def on_message(self, message: discord.Message) -> None:
        if not re.match(self.commandKey, message.content):
            return

        remainString = message.content[len(self.commandKey):]
        sizeStrArray = re.findall("\d+次", remainString)
        if len(sizeStrArray) > 1:
            self.LogI(f"超過一個次 {sizeStrArray}")
            return
        splitArray = remainString.split(" ")
        itemArray = []
        for subString in splitArray:
            if len(subString) != 0:
                itemArray.append(subString)

        if len(sizeStrArray) == 0:
            item = itemArray[random.randrange(len(itemArray))]
            await message.reply(item, mention_author=False)
            return

        randomSize = int(sizeStrArray[0][:-1])
        if itemArray[0][-1] == '次':
            itemArray.pop(0)
        else:
            self.LogI("次後面沒空格的格式不支援")
            return
        itemSize = len(itemArray)

        count = [0] * itemSize
        for _ in range(randomSize):
            count[random.randrange(itemSize)] += 1
        replayStr = ""
        for index in range(itemSize):
            replayStr += f"{itemArray[index]} {count[index]}次\n"
        await message.reply(replayStr, mention_author=False)
