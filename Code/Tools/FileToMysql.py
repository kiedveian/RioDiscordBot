

import sys

import os
import traceback

from dotenv import load_dotenv
from Utility.MysqlManager import MysqlManager


class Setting:
    keyList: list = []
    checkIndex: list = []
    dbPrefix: str = ""
    skipIndex: list = []
    uniqueKeysIndex: list = []
    replaceDatas: list = []


def GetMorningSetting() -> Setting:
    result = Setting()
    result.keyList = ["item_id", "weight", "name",
                      "message", "image", "festival", "festival_hint"]
    result.checkIndex = [0, 2]
    result.dbPrefix = "draw_item_"
    result.uniqueKeysIndex = [0]
    return result


def GetIdiomSetting() -> Setting:
    result = Setting()
    result.keyList = ["idiom", "comment"]
    result.checkIndex = [0]
    result.dbPrefix = "idiom_item_"
    result.uniqueKeysIndex = [0]
    return result


def GetFoolDaySetting() -> Setting:
    result = Setting()
    result.keyList = ["create_time", "author", "nick"]
    result.checkIndex = [2]
    result.skipIndex = [0]
    result.dbPrefix = "festival_2024_fool_day_item_"
    result.uniqueKeysIndex = [2]
    result.replaceDatas = [[2, "\n", ""]]
    return result


def File2Mysql(filePath, tablePostfix, setting: Setting):
    with open(filePath, "r", encoding="utf-8") as file:
        keyList = setting.keyList
        uniqueDatas = []
        for index in setting.uniqueKeysIndex:
            while len(uniqueDatas) <= index:
                uniqueDatas.append({})
        sql = MysqlManager(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user_name=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            schema_name=os.getenv("MYSQL_SCHEMA_NAME")
        )
        selectKeyString = ",".join(keyList)
        insertKeyString = ""
        for index in range(len(keyList)):
            if index in setting.skipIndex:
                continue
            if len(insertKeyString) == 0:
                insertKeyString = keyList[index]
            else:
                insertKeyString = insertKeyString + "," + keyList[index]
        tableName = f"discord_bot.{setting.dbPrefix}{tablePostfix}"
        selectCommand = f"SELECT {selectKeyString} FROM {tableName}"
        selectDatas = sql.SimpleSelect(selectCommand)
        for rowData in selectDatas:
            for index in setting.uniqueKeysIndex:
                uniqueDatas[index][rowData[index]] = True

        sqlArr = []
        count = 0
        for line in file:
            count += 1
            if count == 1:
                continue
            lineSplit = line.split("\t")
            needSkip = False

            for index in setting.checkIndex:
                if len(lineSplit[index]) == 0:
                    needSkip = True
                    break
            for index in setting.uniqueKeysIndex:
                if len(lineSplit[index]) == 0 or lineSplit[index] in uniqueDatas[index]:
                    needSkip = True
                    break
            if needSkip:
                continue
            for index in setting.uniqueKeysIndex:
                if len(lineSplit[index]) != 0:
                    uniqueDatas[index][lineSplit[index]] = True

            lineArr = []
            for index in range(len(keyList)):
                if index in setting.skipIndex:
                    continue
                for replaceArr in setting.replaceDatas:
                    if replaceArr[0] == index:
                        lineSplit[index] = lineSplit[index].replace(
                            replaceArr[1], replaceArr[2])

                lineArr.append(lineSplit[index])
            sqlArr.append(lineArr)

        valueString = "%s"
        for index in range(len(keyList)-1 - len(setting.skipIndex)):
            valueString += " ,%s"
        insertCommand = (f"INSERT INTO {tableName}"
                         f"({insertKeyString})"
                         f"VALUES ({valueString})")
        sql.SimpleCommandMany(insertCommand, sqlArr)


# args = sys.argv[1:]


if __name__ == '__main__':
    print("開始將檔案輸入資料庫")
    load_dotenv()

    if len(sys.argv) < 4:
        print("參數不足")
        ok = False
    else:
        tablePostfix = sys.argv[1]
        dataType = sys.argv[2]
        filePath = sys.argv[3]

        ok = True
        match tablePostfix:
            case "test":
                pass
            case "nerolirain":
                pass
            case _:
                print("資料庫後綴有誤")
                ok = False

        data = None
        match dataType:
            case "draw":
                data = GetMorningSetting()
            case "idiom":
                data = GetIdiomSetting()
            case "fool_day":
                data = GetFoolDaySetting()
            case _:
                print("資料類別有誤")
                ok = False

    if ok:
        try:
            File2Mysql(filePath, tablePostfix, data)
        except Exception:
            print(traceback.format_exc())
        print("檔案輸入資料庫完成")
    else:
        print(sys.argv)
