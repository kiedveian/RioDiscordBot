

import datetime
from inspect import getframeinfo, stack


LOG_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

g_allLogs = []


class Log:

    @staticmethod
    def I(*args, **kwargs):
        for log in g_allLogs:
            log.I(*args, **kwargs)

    @staticmethod
    def W(*args, **kwargs):
        for log in g_allLogs:
            log.W(*args, **kwargs)

    @staticmethod
    def E(*args, **kwargs):
        for log in g_allLogs:
            log.E(*args, **kwargs)


class LogType:
    Undefined = 0
    Info = 1
    Warning = 2
    Error = 3


class LogData:
    logType = LogType.Undefined
    frameInfoData = None
    stackData = None
    message = None
    time = None
    # frameInfoData.filename
    # frameInfoData.lineno

    def __init__(self) -> None:
        self.time = datetime.datetime.utcnow()


class LogToolBase:
    def Log(self, logData: LogData):
        pass

    def I(self, msg: str):
        pass

    def W(self, msg: str):
        pass

    def E(self, msg: str):
        pass


def GetLogData(depth=1, logType=LogType.Undefined) -> LogData:
    result = LogData()
    result.logType = logType
    result.time = datetime.datetime.now()
    stackData = stack()[depth][0]
    result.stackData = stackData
    result.frameInfoData = getframeinfo(stackData)
    return result


class LogToScreen(LogToolBase):

    def __init__(self) -> None:
        super().__init__()

    def Log(self, logData: LogData):
        typeString = ""
        match logData.logType:
            case LogType.Info:
                typeString = "I"
            case LogType.Warning:
                typeString = "W"
            case LogType.Error:
                typeString = "E"
            # case LogType.Undefined:
            #     pass
        # print(logData.logType)
        timeString = logData.time.strftime(LOG_TIME_FORMAT)
        print(f'[%s] %s "%s", line %s, %s' % (typeString, timeString,
              logData.frameInfoData.filename, logData.frameInfoData.lineno, logData.message))

    def I(self, msg: str):
        logData = GetLogData(3, LogType.Info)
        logData.message = msg
        self.Log(logData)

    def W(self, msg: str):
        logData = GetLogData(3, LogType.Warning)
        logData.message = msg
        self.Log(logData)

    def E(self, msg: str):
        logData = GetLogData(3, LogType.Error)
        logData.message = msg
        self.Log(logData)


def AddLogToScreen():
    global g_allLogs
    g_allLogs.append(LogToScreen())


def LogSomethingToScreen(logType, depth, message):
    logData = GetLogData(depth+1, logType)
    logData.message = message
    LogToScreen().Log(logData)

# def debuginfo(message):
#     caller = getframeinfo(stack()[1][0])
#     print("%s:%d - %s" % (caller.filename, caller.lineno, message)) # python3 syntax print

# def grr(arg):
#     debuginfo(arg)      # <-- stack()[1][0] for this line
