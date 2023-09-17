
import datetime
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

CHOICES_REMOVE_EXPIRED = (
    ("1", "不顯示"),
    ("0", "顯示"),
)


class FormParams:
    onlyGuild: bool = False
    orderDesc: bool = True
    removeExpired: bool = True

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.onlyGuild = False
        self.orderDesc = True
        self.removeExpired = True

    def SetData(self, get_request):
        if 'onlyGuildChoice' in get_request:
            self.onlyGuild = get_request['onlyGuildChoice'] == "1"
        if 'orderChoice' in get_request:
            self.orderDesc = get_request['orderChoice'] == "1"
        if 'removeExpired' in get_request:
            self.removeExpired = get_request['removeExpired'] == "1"


class TestForm(forms.Form):
    onlyGuildChoice = forms.ChoiceField(
        label="非森林的貼圖", choices=CHOICES_ONLY_GUILD)
    orderChoice = forms.ChoiceField(label="排序", choices=CHOICES_ORDER_DESC)
    removeExpired = forms.ChoiceField(
        label="過期貼圖", choices=CHOICES_REMOVE_EXPIRED)


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
            row = [-1, item.totalCount, item.name, item.id, memberRow]
            resultList.append(row)
        sortData = sorted(resultList, key=lambda item: item[1], reverse=desc)
        lastCount = -1
        someCount = 1
        rank = 0
        for row in sortData:
            if lastCount == row[1]:
                someCount += 1
            else:
                lastCount = row[1]
                rank += someCount
                someCount = 1
            row[0] = rank
        return sortData


class StickerPageView(TemplateView):

    template_name = "sticker1.html"

    formParams: FormParams = None
    botUpdateTime: datetime.datetime = None
    sql: MysqlManager = None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.formParams = FormParams()
        self.botUpdateTime = None

    def GetSql(self) -> MysqlManager:
        if self.sql == None:
            self.sql = MysqlManager(
                host=os.getenv("MYSQL_HOST"),
                port=int(os.getenv("MYSQL_PORT")),
                user_name=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                schema_name=os.getenv("MYSQL_SCHEMA_NAME")
            )
        return self.sql

    def UpdateBotUpdateTime(self):
        timeCmd = f"SELECT check_time FROM discord_bot.all_sticker WHERE sticker_id = {-NEROLIRAIN_GUILD_ID}"
        subResult = self.GetSql().SimpleSelect(timeCmd)
        if subResult == None:
            print("找不到時間")
            self.botUpdateTime = None
            return None
        self.botUpdateTime = subResult[0][0]

    def GetChooseStickers(self, formParams: FormParams):
        result = {}
        whereString = ""
        if formParams.onlyGuild:
            if len(whereString) == 0:
                whereString += "WHERE "
            else:
                whereString += " AND"
            whereString += f" guild_id = {NEROLIRAIN_GUILD_ID}"

        removeTime = datetime.datetime(2020, 1, 1)
        # 由於同時判定非森林+移除較複雜，改為判定完移除
        if formParams.removeExpired:
            removeTime = self.botUpdateTime
            if removeTime == None:
                print("找不到時間")
                return {}

        command = (f"SELECT sticker_id, name, guild_id, check_time FROM discord_bot.all_sticker"
                   f" {whereString};")

        sqlResult = self.GetSql().SimpleSelect(command)

        for rowData in sqlResult:
            if rowData[2] == 160768297275621376:
                # 測試服
                continue
            if rowData[2] == NEROLIRAIN_GUILD_ID and rowData[3] < removeTime:
                continue
            sticker_id = rowData[0]
            result[sticker_id] = rowData

        return result

    def GetDatas(self, formParams: FormParams):

        dataCommand = (f"SELECT COUNT(0) AS `count`, `stk`.`name`, `log`.`sticker_id`, `log`.`member_nick`, `stk`.`check_time`"
                       f" FROM (`message_log_nerolirain` `log` JOIN `all_sticker` `stk` ON ((`log`.`sticker_id` = `stk`.`sticker_id`)))"
                       f" GROUP BY `log`.`sticker_id`, `log`.`member_id`")

        rowDatas = self.GetSql().SimpleSelect(dataCommand)
        if rowDatas == None:
            return []

        displayStickers = self.GetChooseStickers(formParams)

        trans_map = {}
        for row in rowDatas:
            stk_id = row[2]
            if stk_id not in displayStickers:
                continue
            if stk_id not in trans_map:
                trans_map[stk_id] = StickerItem()
            trans_map[stk_id].AddData(row)

        for stk_id in displayStickers:
            if stk_id > 0 and stk_id not in trans_map:
                item = StickerItem()
                item.id = stk_id
                item.name = displayStickers[stk_id][1]
                trans_map[stk_id] = item

        return StickerItem.ToHtmlDatas(trans_map, formParams.orderDesc)

    def get(self, request, *args, **kwargs):
        if request.GET:
            self.formParams.SetData(request.GET)
        return super().get(request, *args, **kwargs)

    def bool2string(self, data):
        if data:
            return "1"
        return "0"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.UpdateBotUpdateTime()
        context['sticker_datas'] = self.GetDatas(self.formParams)
        timeString = self.botUpdateTime.strftime("%Y-%m-%d %H:%M:%S")
        context['bot_update_time'] = timeString

        form = TestForm(initial={'onlyGuildChoice': self.bool2string(self.formParams.onlyGuild),
                                 'orderChoice': self.bool2string(self.formParams.orderDesc),
                                 'removeExpired': self.bool2string(self.formParams.removeExpired),
                                 })
        context['form'] = form
        return context
