

import discord
from Bot.BotComponent.Base.CompBotBase import CompBotBase


GET_STICKER_COMMAND = "SELECT sticker_id FROM all_sticker"
INSERT_STICKER_COMMAND = "INSERT INTO all_sticker(sticker_id, guild_id, name) VALUES (%s, %s, %s)"


class CompLog(CompBotBase):
    allSticker: set
    insertMessageCommand: str = ""
    insertReactionCommand: str = ""
    insertDmCommand: str = ""

    def Initial(self) -> bool:
        if not super().Initial():
            return False

        self.allSticker = set()
        self.allEvent["on_message"] = True
        self.allEvent["on_raw_reaction_add"] = True

        self._InitCommand()
        self._UpdateStickers()
        return True

    def _UpdateStickers(self):
        stickerDatas = self.sql.SimpleSelect(GET_STICKER_COMMAND)
        self.allSticker = {rowData[0] for rowData in stickerDatas}

    def _InitCommand(self):
        self.insertMessageCommand = (f"INSERT INTO message_log_{self.botSettings.sqlPostfix}"
                                     "(message_id, content, channel_id, channel_name, guild_id, member_id, member_nick, sticker_id, create_time)"
                                     "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ")
        self.insertReactionCommand = (f"INSERT INTO reaction_log_{self.botSettings.sqlPostfix}"
                                      "(message_id, user_id, channel_id)"
                                      "VALUES (%s, %s, %s) ")
        self.insertDmCommand = (f"INSERT INTO dm_log_{self.botSettings.sqlPostfix}"
                                "(message_id, content, channel_id, member_id, member_nick, create_time)"
                                "VALUES (%s, %s, %s, %s, %s, %s) ")

    async def LogMessage(self, message: discord.Message):
        if type(message.channel) is discord.DMChannel:
            # 私訊
            if message.author.bot:
                return
            self.sql.SimpleCommand(self.insertDmCommand, (message.id, message.content, message.channel.id,
                                                          message.author.id, message.author.display_name, message.created_at))
            return

        if len(message.stickers) > 1:
            self.LogW(f"sticker more than one: {len(message.stickers)}")
        stickerId = 0
        for item in message.stickers:
            sticker = await item.fetch()

            if type(sticker) is discord.sticker.GuildSticker:
                stickerId = sticker.id
                if stickerId not in self.allSticker:
                    self.allSticker.add(stickerId)
                    self.sql.SimpleCommand(
                        INSERT_STICKER_COMMAND, (stickerId, sticker.guild_id, sticker.name))

        self.sql.SimpleCommand(self.insertMessageCommand, (message.id, message.content, message.channel.id, message.channel.name,
                               message.guild.id, message.author.id, message.author.display_name, stickerId, message.created_at))

    def LogReaction(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.botClient.user.id:
            return
        self.sql.SimpleCommand(self.insertReactionCommand,
                               (payload.message_id, payload.user_id, payload.channel_id))

    async def on_message(self, message: discord.Message) -> None:
        await self.LogMessage(message=message)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        self.LogReaction(payload)
