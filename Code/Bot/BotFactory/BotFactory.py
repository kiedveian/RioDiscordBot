

from Bot.BotFactory.BotBase import BotBase
from Bot.BotFactory.BotNerolirain import BotNerolirain
from Bot.BotFactory.BotMei import BotMei
from Bot.BotFactory.BotTest import BotTest
from Utility.DebugTool import Log


def CreateBot(name: str):
    match name:
        case "nerolirain":
            return BotNerolirain()
        case "mei":
            return BotMei()
        case "test":
            return BotTest()
    Log.W(f"unknow bot name: {name}")
    return None
