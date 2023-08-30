
import os
from typing import Any, Mapping, Optional, Type, Union
from django.forms.utils import ErrorList
from django.views.generic import TemplateView
from django import forms

from Utility.MysqlManager import MysqlManager


NEROLIRAIN_GUILD_ID = 824892342455500800

CHOICES_ONLY_GUILD = (
    ("0", "顯示"),
    ("1", "不顯示"),
)

CHOICES_ORDER_DESC = (
    ("1", "由大至小"),
    ("0", "由小至大"),
)


class TestForm(forms.Form):
    onlyGuildChoice = forms.ChoiceField(
        label="非森林的貼圖", choices=CHOICES_ONLY_GUILD)
    orderChoice = forms.ChoiceField(label="排序", choices=CHOICES_ORDER_DESC)


class MemberData:
    nick: str = "unknow"
    count: int


class StickerItem:
    id: int
    name: str
    totalCount: int

    memberDatas = []

    def __init__(self) -> None:
        self.id = 0
        self.name = "unknow"
        self.totalCount = 0
        self.memberDatas = []

    def AddData(self, rowData):
        id = rowData[2]
        if self.id == 0:
            self.id = id
            self.name = rowData[1]
        elif self.id != id:
            print(f"StickerItem id error {self.id}, {id}")
        memberData = MemberData()
        memberData.count = rowData[0]
        memberData.nick = rowData[3]
        self.memberDatas.append(memberData)
        self.totalCount += memberData.count

    def ToHtmlDatas(itemsMap, desc=True):
        resultList = []
        for id in itemsMap:
            item = itemsMap[id]
            memberRow = []
            for member in item.memberDatas:
                memberRow.append([member.count, member.nick])
            memberRow = sorted(
                memberRow, key=lambda member: member[0], reverse=True)
            row = [item.totalCount, item.name, item.id, memberRow]
            resultList.append(row)
        return sorted(resultList, key=lambda item: item[0], reverse=desc)


class StickerPageView(TemplateView):

    template_name = "sticker1.html"

    onlyGuild = False
    orderDesc = True

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.onlyGuild = False
        self.orderDesc = True

    def GetDatas(self, onlyGuild=False, desc=True):
        sql = MysqlManager(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user_name=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            schema_name=os.getenv("MYSQL_SCHEMA_NAME")
        )
        # command = f"SELECT user_id, draw_alarm_message FROM user_data_{self.botSettings.sqlPostfix} WHERE draw_alarm_message != 0"
        # command = (f"SELECT COUNT(0) AS `count`, `stk`.`name`, `log`.`sticker_id`
        #            f" FROM (`message_log_nerolirain` `log` JOIN `all_sticker` `stk` ON ((`log`.`sticker_id` = `stk`.`sticker_id`)))"
        #            f" WHERE (`stk`.`guild_id` = 824892342455500800)"
        #            f" GROUP BY `log`.`sticker_id` ORDER BY `count` DESC"
        #            )

        guildString = ""
        if onlyGuild:
            guildString = f" WHERE (`stk`.`guild_id` = {NEROLIRAIN_GUILD_ID})"

        dataCommand = (f"SELECT COUNT(0) AS `count`, `stk`.`name`, `log`.`sticker_id`, `log`.`member_nick`"
                       f" FROM (`message_log_nerolirain` `log` JOIN `all_sticker` `stk` ON ((`log`.`sticker_id` = `stk`.`sticker_id`)))"
                       "%s"
                       f" GROUP BY `log`.`sticker_id`, `log`.`member_id`"
                       % (guildString))

        all_datas = sql.SimpleSelect(dataCommand)

        trans_map = {}
        for data in all_datas:
            stk_id = data[2]
            if stk_id not in trans_map:
                trans_map[stk_id] = StickerItem()
            trans_map[stk_id].AddData(data)

        if onlyGuild:
            allStickerCommand = (f"SELECT sticker_id, name FROM discord_bot.all_sticker WHERE guild_id = {NEROLIRAIN_GUILD_ID};")
            allSticker = sql.SimpleSelect(allStickerCommand)
            
            for rowData in allSticker:
                sticker_id = rowData[0]
                if sticker_id not in trans_map:
                    item = StickerItem()
                    item.id = sticker_id
                    item.name = rowData[1]
                    trans_map[sticker_id] = item
        return StickerItem.ToHtmlDatas(trans_map, desc)

    def get(self, request, *args, **kwargs):
        if request.GET:
            self.onlyGuild = request.GET['onlyGuildChoice'] == "1"
            self.orderDesc = request.GET['orderChoice'] == "1"
        return super().get(request, *args, **kwargs)

    def bool2string(self, data):
        if data:
            return "1"
        return "0"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sticker_datas'] = self.GetDatas(
            onlyGuild=self.onlyGuild, desc=self.orderDesc)
        
        form = TestForm(initial={'onlyGuildChoice': self.bool2string(self.onlyGuild),
                                 'orderChoice': self.bool2string(self.orderDesc)
                                 })
        context['form'] = form
        return context
