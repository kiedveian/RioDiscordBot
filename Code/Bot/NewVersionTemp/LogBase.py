

from Utility.DebugTool import Log, LogToolGeneral


class LogBase():
    DEFAULT_LOG_DEPTH = LogToolGeneral.DEFAULT_LOG_DEPTH + 1

    def _GetLogDepth(self, **kwargs):
        depth = LogBase.DEFAULT_LOG_DEPTH
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

    def LogException(self, *args, **kwargs):
        Log.E(depth=self._GetLogDepth(**kwargs) + 1, *args, **kwargs)
