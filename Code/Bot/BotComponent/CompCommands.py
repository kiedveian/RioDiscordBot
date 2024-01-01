

import datetime
import re
import discord
from Bot.BotComponent.Base.CompBotBase import CompBotBase
from Bot.NewVersionTemp.CompBase2024 import CompBase

SQL_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class CompCommands(CompBase):
    commandColseAll = ""
    commandColseTime = ""

    def Initial(self) -> bool:
        if not super().Initial():
            return False

        self.commandColseAll = f"SELECT * FROM discord_bot.view_totoal_close_time_{self.botSettings.sqlPostfix};"
        self.commandColseTime = (f" SELECT `log`.`user_id` AS `user_id`, `all_user`.`nick` AS `nick`"
                                 f" ,ROUND((SUM(`log`.`delta_time`) / 60.0), 1) AS `total_time(min)`"
                                 f" ,COUNT(*) AS `cnt`"
                                  f"  FROM (`close_log_{self.botSettings.sqlPostfix}` `log`"
                                 f"   LEFT JOIN `all_user` ON((`log`.`user_id`= `all_user`.`user_id`)))"
                                 f" WHERE `log`.`event_time` > '%s' AND `log`.`event_time` < '%s'"
                                 f" GROUP BY `log`.`user_id`"
                                 f" ORDER BY `total_time(min)` DESC")

        self.allEvent["on_message"] = True
        return True

    async def on_message(self, message: discord.Message) -> None:
        if re.match("!小黑屋統計", message.content):
            datas = None
            title = ""
            if re.search("一週", message.content) != None:
                endTime = (datetime.datetime.now()).strftime(SQL_TIME_FORMAT)
                startTime = (datetime.datetime.now() -
                             datetime.timedelta(days=7)).strftime(SQL_TIME_FORMAT)
                datas = self.sql.SimpleSelect(
                    self.commandColseTime % (startTime, endTime))
                title = f"顯示台灣時間(GMT+8) {startTime} 至 {endTime} 的資料"
            else:
                datas = self.sql.SimpleSelect(self.commandColseAll)
            await self.ReplyResult(message, datas, title=title, count=3)
            return

    async def ReplyResult(self, message: discord.Message, datas, title="", count=3):
        if datas == None:
            self.LogW("資料異常")
            return
        noEnough = False
        if len(datas) < count:
            count = len(datas)
            noEnough = True
        resultString = ""
        for index in range(count):
            # user_id, nick total_time(min)
            rowData = datas[index]
            member = await self.botClient.GetGuild().fetch_member(rowData[0])
            resultString += f"\n第{index+1}名 {rowData[2]}分({rowData[3]}次) {member.display_name}({member.name})"

        if noEnough:
            resultString += f"\n第{count+1}名 從缺"

        embed = discord.Embed(title=title, description=resultString, color=0x5acef5)
        await message.reply(embed=embed, mention_author=False)
