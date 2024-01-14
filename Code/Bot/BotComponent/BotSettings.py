

import datetime
from Utility.DebugTool import Log
from Utility.MysqlManager import MysqlManager


def GetTransData(setting_datas):
    trans_data = {}
    trans_data["MORNING_TIME_USER_LIST"] = []
    trans_data["CLOSE_AVOID_HINT_USER_LIST"] = []
    trans_data["DRAW_ADMIN_LIST"] = []
    for line_data in setting_datas:
        if line_data[0] not in trans_data:
            trans_data[line_data[0]] = []
        value = line_data[1]
        match line_data[2]:
            case "int":
                value = int(value)
            case "string":
                pass
            case "rio-time":
                value = datetime.datetime.strptime(
                    value, '%Y-%m-%d %H:%M').replace(tzinfo=datetime.timezone(datetime.timedelta(hours=8)))
            case _:
                Log.E("error type: " + value + ", type: " + line_data[2])
        trans_data[line_data[0]].append(value)
    return trans_data


class BotSettings:
    sqlPostfix = None

    def __init__(self, key: str) -> None:
        self.sqlPostfix = key

    def LoadSettings(self, sql: MysqlManager):
        command = f"SELECT data_name, data_value, data_type FROM setting_{self.sqlPostfix} where data_enable = 1;"
        setting_datas = sql.SimpleSelect(command)
        trans_data = GetTransData(setting_datas)
        self.SetAllDatas(trans_data)

    def SetDict(self, trans_data, valueName, key, index=-1):
        value = None
        if key in trans_data:
            if index == -1:
                value = trans_data[key]
            elif index < len(trans_data[key]):
                value = trans_data[key][index]

        if value == None:
            Log.W(f"settings no find {key} {index}")
            return
        self.__dict__[valueName] = value

    def SetAllDatas(self, trans_data):
        self.SetDict(trans_data, "botToken", "BOT_TOKEN", 0)

        self.SetDict(trans_data, "closeReatcionList", "CLOSE_REACTION_LIST")

        self.SetDict(trans_data,
                     "closeReatcionCount", "CLOSE_REACTION_COUNT", 0)
        self.SetDict(trans_data, "closeServerId", "CLOSE_SERVER_ID", 0)
        self.SetDict(trans_data, "closeChannelId", "CLOSE_CHANNEL_ID", 0)
        self.SetDict(trans_data, "closeIgnoreTime", "CLOSE_IGNORE_TIME", 0)
        self.SetDict(trans_data, "closeBossId", "CLOSE_BOSS_ID", 0)
        self.SetDict(trans_data, "closeBotId", "CLOSE_BOT_ID", 0)
        self.SetDict(trans_data, "closeEventType", "CLOSE_EVENT_TYPE", 0)
        self.SetDict(trans_data, "closeRoleId", "CLOSE_ROLE_ID", 0)
        self.SetDict(trans_data,
                     "closeTimeMaxSecond", "CLOSE_TIME_MAX_SECOND", 0)
        self.SetDict(trans_data,
                     "closeTimeColdDownSecond", "CLOSE_TIME_COLD_DOWN_SECOND", 0)
        self.SetDict(trans_data, "closeKeyString", "CLOSE_KEY_STRING", 0)
        self.SetDict(trans_data,
                     "closeAvoidHintUserList", "CLOSE_AVOID_HINT_USER_LIST")
        self.SetDict(trans_data, "closeTicketId", "CLOSE_TICKET_ID", 0)

        self.SetDict(trans_data, "morningChannelId", "MORNING_CHANNEL_ID", 0)
        self.SetDict(trans_data,
                     "morningTimeUserList", "MORNING_TIME_USER_LIST")
        self.SetDict(trans_data, "morningReplayKey", "MORNING_REPLAY_KEY", 0)

        self.SetDict(trans_data, "drawChannel", "DRAW_CHANNEL_ID", 0)
        self.SetDict(trans_data,
                     "drawAdminChannel", "DRAW_ADMIN_CHANNEL_ID", 0)
        self.SetDict(trans_data, "drawAdminList", "DRAW_ADMIN_LIST")

        self.SetDict(trans_data, "idiomChannel", "IDIOM_CHANNEL_ID", 0)
        self.SetDict(trans_data, "idiomCooldownSecond", "IDIOM_COOLDOWN_SECOND", 0)

        self.SetDict(trans_data, "blessChannel", "BLESS_CHANNEL", 0)
        self.SetDict(trans_data, "festivalChannel", "FESTIVAL_CHANNEL", 0)
