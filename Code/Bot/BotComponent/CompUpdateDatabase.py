

import datetime
from Bot.BotComponent.Base.CompBotBase import CompBotBase
from Bot.NewVersionTemp.CompBase2024 import CompBase


class CompUpdateDatabase(CompBase):

    def SetComponents(self, bot):
        return super().SetComponents(bot)

    def Initial(self) -> bool:
        if not super().Initial():
            return False

        self.allEvent["on_ready"] = True
        return True

    async def on_ready(self) -> None:
        guild = self.botClient.GetGuild()
        if guild == None:
            return
        guildId = guild.id

        nowTime = datetime.datetime.now()
        timeData = nowTime

        selectCommand = (f"SELECT sticker_id, guild_id FROM all_sticker;")
        selectResult = self.sql.SimpleSelect(selectCommand)
        sqlSitckers = {}
        for row in selectResult:
            if row[1] == guildId:
                sqlSitckers[row[0]] = row[1]

        insertCommand = (f"INSERT INTO all_sticker"
                         " (sticker_id, guild_id, name, check_time)"
                         " VALUES(%s, %s, %s, %s)")
        updateCommand = (f"UPDATE all_sticker "
                         f"SET check_time=%s"
                         f"WHERE sticker_id=%s")
        insertDatas = []
        updateDatas = [[timeData, -guildId]]
        for sticker in guild.stickers:
            stickerId = sticker.id
            if stickerId in sqlSitckers:
                updateDatas.append([timeData, stickerId])
            else:
                name = sticker.name
                insertDatas.append([stickerId, guildId, name, timeData])

        self.sql.SimpleCommandMany(insertCommand, insertDatas)
        self.sql.SimpleCommandMany(updateCommand, updateDatas)
