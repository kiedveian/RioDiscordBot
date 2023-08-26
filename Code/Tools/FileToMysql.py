

import sys

import os
import traceback

from dotenv import load_dotenv
from Utility.MysqlManager import MysqlManager

DRAW_DATA = ["item_id", "weight", "name", "message",
             "image", "festival", "festival_hint"]


class DataType:
    DRAW = 1


def File2Mysql(filePath, refData, tablePostfix):
    with open(filePath, "r", encoding="utf-8") as file:
        sqlArr = []
        count = 0
        for line in file:
            count += 1
            if count == 1:
                continue
            lineSplit = line.split("\t")
            lineArr = []
            for index in range(len(refData)):
                lineArr.append(lineSplit[index])
            sqlArr.append(lineArr)

        keyString = ",".join(refData)
        valueString = "%s"
        for index in range(len(refData)-1):
            valueString += " ,%s"
        command = (f"INSERT INTO discord_bot.draw_item_{tablePostfix}"
                   f"({keyString})"
                   f"VALUES ({valueString})")
        sql = MysqlManager(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user_name=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            schema_name=os.getenv("MYSQL_SCHEMA_NAME")
        )
        sql.SimpleCommandMany(command, sqlArr)


# args = sys.argv[1:]


if __name__ == '__main__':
    print("開始將檔案輸入資料庫")
    load_dotenv()

    if len(sys.argv) < 4:
        print("參數不足")
        ok = False
    else:
        tablePostfix = sys.argv[1]
        dataType = int(sys.argv[2])
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

        refData = None
        match dataType:
            case 1:
                refData = DRAW_DATA
            case _:
                print("資料類別有誤")
                ok = False

    # filename = "../Files/draw/抽抽 - 工作表1.tsv"
    # filePath = "Files/sql/draw/20230821.tsv"
    # filePath = "../../../Files/sql/draw/20230821.tsv"
    # dataType = 1
    # tablePostfix = "test"

    if ok:
        try:
            File2Mysql(filePath, refData, tablePostfix)
        except Exception:
            print(traceback.format_exc())
        print("檔案輸入資料庫完成")
    else:
        print(sys.argv)