

from Bot.BotComponent.BotClient import BotClient
from Bot.BotComponent.BotSettings import BotSettings
from Utility.DebugTool import Log, LogToolGeneral
from Utility.MysqlManager import MysqlManager


class CompBase:
    DEFAULT_LOG_DEPTH = LogToolGeneral.DEFAULT_LOG_DEPTH + 1
    isInitailized: bool = False

    allEvent = {}

    def __init__(self) -> None:
        self.isInitailized = False
        self.allEvent = {}

    def SetComponents(self, bot):
        pass

    def IsInitialized(self) -> bool:
        return self.isInitailized

    def CanInitial(self) -> bool:
        return True

    def Initial(self) -> bool:
        # 初始化，由於可能會相其他組件
        self.isInitailized = True
        return self.isInitailized

    def HasEvent(self, key):
        result = (key in self.allEvent) and self.allEvent[key]
        if result:
            invert_op = getattr(self, key, None)
            if not callable(invert_op):
                self.LogW("找不到函式:", key, self)
        return result

    def _GetLogDepth(self, **kwargs):
        depth = CompBase.DEFAULT_LOG_DEPTH
        if "depth" in kwargs:
            depth = kwargs["depth"]
            del kwargs["depth"]
        return depth

    def LogI(self, *args,  **kwargs):
        Log.I(depth=self._GetLogDepth(**kwargs), *args, **kwargs)

    def LogW(self, *args, **kwargs):
        Log.W(depth=self._GetLogDepth(**kwargs), *args, **kwargs)

    def LogE(self, *args, **kwargs):
        Log.E(depth=self._GetLogDepth(**kwargs), *args, **kwargs)
