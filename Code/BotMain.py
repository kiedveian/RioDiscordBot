

import asyncio
import datetime
import sys
import traceback

from Utility.DebugTool import AddLogToFile, AddLogToScreen, Log


g_bot = None


async def BackgroundTask():
    Log.I("背景程式執行時間 %s" % (datetime.datetime.today()))
    while not g_bot.isReady:
        await asyncio.sleep(1)
    Log.I("初始完畢")
    errorCount = 0
    while errorCount < 10:
        try:
            await g_bot.PreSecondEvent()
        except Exception:
            errorCount = errorCount + 1
            Log.E(traceback.format_exc())
        await asyncio.sleep(1)
    Log.I(f"背景程式結束 錯誤數量:{errorCount}")


async def RunTask():
    asyncio.create_task(BackgroundTask())
    await g_bot.Start()


async def MyMain(argv):
    AddLogToScreen()
    timeString = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    AddLogToFile(f"Files/logs/{timeString}.log")
    postfix = argv[1]
    botName = argv[2]

    Log.I(f"sql postfix: {postfix}")

    # g_bot = CreateBot(botName)
    # if g_bot == None:
    #     print(f"bot name error {botName}")
    # else:
    #     g_bot.SetData(postfix)
    #     asyncio.run(MyMain())

if __name__ == '__main__':
    asyncio.run(MyMain(sys.argv))
