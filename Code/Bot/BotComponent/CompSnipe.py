

import re
import discord
from Bot.BotComponent.Base.CompBotBase import CompBotBase


class CompSnipe(CompBotBase):
    removeMessages = {}
    editMessages = {}

    def Initial(self) -> bool:
        if not super().Initial():
            return False

        self.allEvent["on_message"] = True
        self.allEvent["on_raw_message_delete"] = True
        self.allEvent["on_raw_message_edit"] = True

        return True

    async def ReplyRemoveMessage(self, message: discord.Message):
        # TODO lock
        removePayload: discord.RawMessageDeleteEvent = self.removeMessages[message.channel.id]
        if removePayload.cached_message != None:
            removeMsg = removePayload.cached_message
            title = f"{removeMsg.author.display_name}({removeMsg.author.name})"
            embed = discord.Embed(title=title, color=0x3498db)
            embed.add_field(name="刪除的訊息", value=removeMsg.content)
            await message.reply(embed=embed, mention_author=False)
        else:
            await message.reply(content="找不到刪除的訊息", mention_author=False)

    async def ReplyEditMessage(self, message: discord.Message):
        # TODO lock
        editPayload: discord.RawMessageUpdateEvent = self.editMessages[message.channel.id]
        if editPayload.cached_message != None:
            editMsg = editPayload.cached_message
            title = f"{editMsg.author.display_name}({editMsg.author.name})"
            embed = discord.Embed(title=title, color=0x3498db)
            embed.add_field(name="原本的訊息", value=editMsg.content, inline=False)
            if "content" in editPayload.data:
                embed.add_field(
                    name="修改的訊息", value=editPayload.data["content"], inline=False)
            await message.reply(embed=embed, mention_author=False)
        else:
            await message.reply(content="找不到編輯的訊息", mention_author=False)

    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        # TODO 檢查嵌入式
        if payload.cached_message != None:
            if payload.cached_message.author.bot:
                self.LogI("on_raw_message_edit skip bot")
                return
        self.editMessages[payload.channel_id] = payload
        # print("on_raw_message_edit")

    async def on_message(self, message: discord.Message) -> None:
        if re.match("!snipe", message.content):
            if message.channel.id in self.removeMessages:
                await self.ReplyRemoveMessage(message=message)
            else:
                await message.reply(content="找不到刪除的訊息", mention_author=False)

        if re.match("!esnipe", message.content):
            if message.channel.id in self.editMessages:
                await self.ReplyEditMessage(message=message)
            else:
                await message.reply(content="找不到編輯的訊息", mention_author=False)

    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        if payload.cached_message != None:
            if payload.cached_message.author.bot:
                self.LogI("on_raw_message_delete skip bot")
                return
        self.removeMessages[payload.channel_id] = payload
        # print("on_raw_message_delete")
