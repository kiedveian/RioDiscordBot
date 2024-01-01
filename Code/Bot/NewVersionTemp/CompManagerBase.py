
from Bot.NewVersionTemp.CompBase2024 import CompBase


class CompManagerBase:
    allComp = {}

    def __init__(self, *args, **kwargs) -> None:
        self.allComp = {}

    def _AddAllComponents(self):
        # 加入需要的組件
        pass

    def _SetAllComponentInitial(self):
        remainComp = []
        for key in self.allComp:
            comp = self.allComp[key]
            if isinstance(comp, CompBase):
                comp.SetComponents(self)
                remainComp.append(comp)
        tryCount = 0
        while tryCount < 100 and len(remainComp) != 0:
            tryCount += 1
            nextComp = []
            for comp in remainComp:
                # comp: CompBase = comp
                if comp.CanInitial():
                    if not comp.Initial():
                        nextComp.append(comp)
                else:
                    nextComp.append(comp)

            remainComp = nextComp
        if len(remainComp) != 0:
            failList = []
            for key in self.allComp:
                if isinstance(self.allComp[key], CompBase):
                    if not self.allComp[key].IsInitialized():
                        failList.append(key)
            self.LogW(f"組件未初始化: {failList}, 嘗試次數: {tryCount}")

    def GetComponent(self, key: str):
        if key in self.allComp:
            return self.allComp[key]
        self.LogW(f"no find component: {key}")
        return None

    def AddComponent(self, key: str, comp):
        if key in self.allComp:
            self.LogW(f"{key} 已存在資料: ", self.allComp[key])
        self.allComp[key] = comp
