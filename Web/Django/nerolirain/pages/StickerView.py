
import datetime
import os
from typing import Any, Dict, Mapping, Optional, Type, Union
from django.forms.utils import ErrorList
from django.views.generic import TemplateView
from django import forms
from django.db import models

from Utility.MysqlManager import MysqlManager


NEROLIRAIN_GUILD_ID = 824892342455500800

FORM_TIME_FORMAT = "%Y-%m-%dT%H:%M"
SQL_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
ALL_TIME_START = datetime.datetime(2000, 1, 1).strftime(FORM_TIME_FORMAT)
ALL_TIME_END = datetime.datetime(
    2099, 12, 31, 23, 59, 59).strftime(FORM_TIME_FORMAT)
LOCAL_TO_UTC_SHIFT_TIME = datetime.timedelta(hours=-8)


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

SELECT_DATETIME_ALL = "任意時間"
SELECT_DATETIME_NEAREST_WEEK = "最近一週"
SELECT_DATETIME_NEAREST_30DAYS = "最近30天"
SELECT_DATETIME_CUSTOM = "自訂時間"
SELECT_BUTTON_LIST = [SELECT_DATETIME_ALL, SELECT_DATETIME_NEAREST_WEEK, 
                      SELECT_DATETIME_NEAREST_30DAYS, SELECT_DATETIME_CUSTOM]


def bool2string(data):
    if data:
        return "1"
    return "0"


class FormParams:
    onlyGuild: bool = False
    orderDesc: bool = True
    removeExpired: bool = True
    startTime: str = ALL_TIME_START
    endTime: str = ALL_TIME_END
    timeRange: str = "全部"

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
        if 'timeRange' in get_request:
            submit = get_request['timeRange']
            self.timeRange = submit
            if submit == SELECT_DATETIME_ALL:
                self.startTime = ALL_TIME_START
                self.endTime = ALL_TIME_END
            elif submit == SELECT_DATETIME_NEAREST_WEEK:
                now = datetime.datetime.now()
                startTime = now + datetime.timedelta(days=-7)
                self.startTime = startTime.strftime(FORM_TIME_FORMAT)
                self.endTime = now.strftime(FORM_TIME_FORMAT)
            elif submit == SELECT_DATETIME_NEAREST_30DAYS:
                now = datetime.datetime.now()
                startTime = now + datetime.timedelta(days=-30)
                self.startTime = startTime.strftime(FORM_TIME_FORMAT)
                self.endTime = now.strftime(FORM_TIME_FORMAT)
            elif submit == SELECT_DATETIME_CUSTOM:
                if 'startTime' in get_request:
                    self.startTime = get_request['startTime']
                if 'endTime' in get_request:
                    self.endTime = get_request['endTime']


class FormModel(models.Model):
    pass


class SelectForm(forms.ModelForm):
    class Meta:
        model = FormModel
        fields = []

    def __init__(self, *args, **kwargs):
        formParams = FormParams()
        if "formParams" in kwargs:
            formParams = kwargs.pop("formParams")

        super().__init__(*args, **kwargs)

        self.fields.update({
            'onlyGuildChoice': forms.ChoiceField(choices=CHOICES_ONLY_GUILD, initial=bool2string(formParams.onlyGuild)),
            'orderChoice': forms.ChoiceField(choices=CHOICES_ORDER_DESC, initial=bool2string(formParams.orderDesc)),
            'removeExpired': forms.ChoiceField(choices=CHOICES_REMOVE_EXPIRED, initial=bool2string(formParams.removeExpired)),
            'startTime': forms.DateTimeField(widget=forms.DateTimeInput(format=FORM_TIME_FORMAT, attrs={'type': 'datetime-local', 'value': formParams.startTime})),
            'endTime': forms.DateTimeField(widget=forms.DateTimeInput(format=FORM_TIME_FORMAT, attrs={'type': 'datetime-local', 'value': formParams.endTime})),
        })


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

        whereString = ""
        if formParams.startTime != ALL_TIME_START:
            startTime = datetime.datetime.strptime(
                formParams.startTime, FORM_TIME_FORMAT)
            startTime += LOCAL_TO_UTC_SHIFT_TIME
            startTimeString = startTime.strftime(SQL_TIME_FORMAT)
            whereString = f'WHERE create_time >= "{startTimeString}"'

        if formParams.endTime != ALL_TIME_END:
            if len(whereString) == 0:
                whereString = f"WHERE "
            else:
                whereString += " AND "
            endTime = datetime.datetime.strptime(
                formParams.endTime, FORM_TIME_FORMAT)
            endTime += LOCAL_TO_UTC_SHIFT_TIME
            endTime = endTime.replace(second=59)
            endTimeString = endTime.strftime(SQL_TIME_FORMAT)
            whereString += f' create_time <= "{endTimeString}"'

        dataCommand = (f"SELECT COUNT(0) AS `count`, `stk`.`name`, `log`.`sticker_id`, `log`.`member_nick`, `stk`.`check_time`"
                       f" FROM (`message_log_nerolirain` `log` JOIN `all_sticker` `stk` ON ((`log`.`sticker_id` = `stk`.`sticker_id`)))"
                       f" {whereString}"
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

        # 補上 0 次的森林貼圖
        for stk_id in displayStickers:
            if stk_id > 0 and stk_id not in trans_map:
                if displayStickers[stk_id][2] != NEROLIRAIN_GUILD_ID:
                    continue
                item = StickerItem()
                item.id = stk_id
                item.name = displayStickers[stk_id][1]
                trans_map[stk_id] = item

        return StickerItem.ToHtmlDatas(trans_map, formParams.orderDesc)

    def get(self, request, *args, **kwargs):
        if request.GET:
            self.formParams.SetData(request.GET)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.UpdateBotUpdateTime()
        context['sticker_datas'] = self.GetDatas(self.formParams)
        timeString = self.botUpdateTime.strftime("%Y-%m-%d %H:%M:%S")
        context['bot_update_time'] = timeString

        newForm = SelectForm(formParams=self.formParams)
        context['form'] = newForm
        context['botton_list'] = SELECT_BUTTON_LIST
        return context
