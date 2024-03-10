

from Bot.NewVersionTemp.CompBase2024 import CompBase


class FestivalId:
    APRIL_FOOL_DAY_2024 = 1


class CogFestivalDatas(CompBase):
    def GetFestivalName(self, id):
        match id:
            case FestivalId.APRIL_FOOL_DAY_2024:
                return "愚人節2024"
            case _:
                self.LogW("unknow festival id ", id)
                return "unknow"

    def GetDatas(self, festivalId):
        command = (f"SELECT data_id, data_key, data_value"
                   f" FROM festival_all_data_{self.botSettings.sqlPostfix}"
                   f" WHERE festival_id = {festivalId}")

        allQuery = self.sql.SimpleSelect(command)
        result = {}
        for arr in allQuery:
            if arr[0] not in result:
                result[arr[0]] = {}
            result[arr[0]][arr[1]] = arr[2]
        return result

    def InsertOrUpdateData(self, festivalId, dataId, dataKey, value):
        selectCommand = (f"SELECT id"
                         f" FROM festival_all_data_{self.botSettings.sqlPostfix}"
                         f" WHERE festival_id = %s AND data_id = %s AND data_key = %s")
        selectDatas = self.sql.SimpleSelect(
            selectCommand, (festivalId, dataId, dataKey))
        if len(selectDatas) == 0:
            command = (f"INSERT INTO festival_all_data_{self.botSettings.sqlPostfix}"
                       f" (festival_id, data_id, data_key, data_value)"
                       f" VALUES (%s,%s,%s,%s)")
            self.sql.SimpleCommand(
                command, (festivalId, dataId, dataKey, value))
        else:
            rowId = selectDatas[0][0]
            command = (f"UPDATE festival_all_data_{self.botSettings.sqlPostfix}"
                       f" SET data_value = %s"
                       f" WHERE id = %s")
            self.sql.SimpleCommand(command, (value, rowId))
