

import datetime
from inspect import getframeinfo, stack
import io

from colorama import Fore, Style


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

    def __init__(self) -> None:
        self.time = datetime.datetime.utcnow()


class LogToolBase:
    def Log(self, logData: LogData):
        pass

    def I(self, msg: str, *args, **kwargs):
        pass

    def W(self, msg: str, *args, **kwargs):
        pass

    def E(self, msg: str, *args, **kwargs):
        pass


class LogToolGeneral(LogToolBase):
    DEFAULT_LOG_DEPTH = 3

    def I(self, msg: str, *args, **kwargs):
        depth = LogToolGeneral.DEFAULT_LOG_DEPTH
        if "depth" in kwargs:
            depth = kwargs["depth"]
        logData = GetLogData(depth, LogType.Info)
        logData.message = msg
        self.Log(logData, *args, **kwargs)

    def W(self, msg: str, *args, **kwargs):
        depth = LogToolGeneral.DEFAULT_LOG_DEPTH
        if "depth" in kwargs:
            depth = kwargs["depth"]
        logData = GetLogData(depth, LogType.Warning)
        logData.message = msg
        self.Log(logData, *args, **kwargs)

    def E(self, msg: str, *args, **kwargs):
        depth = LogToolGeneral.DEFAULT_LOG_DEPTH
        if "depth" in kwargs:
            depth = kwargs["depth"]
        logData = GetLogData(depth, LogType.Error)
        logData.message = msg
        self.Log(logData, *args, **kwargs)


def GetLogData(depth=1, logType=LogType.Undefined) -> LogData:
    result = LogData()
    result.logType = logType
    result.time = datetime.datetime.now()
    stackData = stack()[depth][0]
    result.stackData = stackData
    result.frameInfoData = getframeinfo(stackData)
    return result


class LogToScreen(LogToolGeneral):

    def __init__(self) -> None:
        super().__init__()

    def Log(self, logData: LogData, *args, **kwargs):
        typeString = ""
        colorString = ""
        resetColorString = ""
        match logData.logType:
            case LogType.Info:
                typeString = "I"
            case LogType.Warning:
                typeString = "W"
                colorString = Fore.YELLOW
                resetColorString = Style.RESET_ALL
            case LogType.Error:
                typeString = "E"
                colorString = Fore.RED
                resetColorString = Style.RESET_ALL
            # case LogType.Undefined:
            #     pass
        # print(logData.logType)
        timeString = logData.time.strftime(LOG_TIME_FORMAT)

        if "depth" in kwargs:
            del kwargs["depth"]
        filename = logData.frameInfoData.filename
        lineno = logData.frameInfoData.lineno

        print((f'[{typeString}] {timeString} "{filename}", line {lineno}, \n'
               f'{colorString}'
               f'    {logData.message}'),
              *args, resetColorString, **kwargs)


class LogToFile(LogToolGeneral):
    file = None

    def __init__(self) -> None:
        super().__init__()

    def Log(self, logData: LogData, *args, **kwargs):
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
        timeString = logData.time.strftime(LOG_TIME_FORMAT)

        if "depth" in kwargs:
            del kwargs["depth"]
        filename = logData.frameInfoData.filename
        lineno = logData.frameInfoData.lineno
        print((f'[{typeString}] {timeString} "{filename}", line {lineno}, \n'
               f'    {logData.message}'),
              *args, file=self.file, **kwargs)

        self.file.flush()

    def SetFile(self, filename: str):
        self.file = open(filename, 'a', encoding='UTF-8')


def AddLogToScreen():
    global g_allLogs
    g_allLogs.append(LogToScreen())


def AddLogToFile(filename):
    global g_allLogs
    logger = LogToFile()
    logger.SetFile(filename)
    g_allLogs.append(logger)


def LogSomethingToScreen(logType, depth, message):
    logData = GetLogData(depth+1, logType)
    logData.message = message
    LogToScreen().Log(logData)

# def debuginfo(message):
#     caller = getframeinfo(stack()[1][0])
#     print("%s:%d - %s" % (caller.filename, caller.lineno, message)) # python3 syntax print

# def grr(arg):
#     debuginfo(arg)      # <-- stack()[1][0] for this line
