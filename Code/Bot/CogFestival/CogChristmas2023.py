

import random
import discord
from discord.commands import SlashCommandGroup

from Bot.Cogs.CogBase import CogBase
from Bot.SlashCommand.CommandsBot import CommandsBot

# 記錄每個人的故事與賜福
# 抽取故事
# 猜某個人(選取森林伺服器的一個人)
# 暱稱冠上祝福，猜中-冠上自己，猜錯-冠上隨機一人
# (選用功能)：有「是否為處罰」欄位-若為真或1，上方猜中與猜錯結果相反

TEST_USER_LIST = [
    824282959572893696,
    160763041447804938,
]


class ChristmasItem:
    id: int
    member:discord.Member
    message: str
    bless: str


class CogChristmas2023(CogBase):
    allItems = []
    allLogsById = {}
    itemState = {}

    # 輔助搜尋
    mapNameToMember = {}
    allLogsByDrawId = {}

    def __init__(self, bot: CommandsBot):
        super().__init__(bot)

    def Initial(self) -> bool:
        if not super().Initial():
            return False
        self.LoadItems()
        self.LoadLogs()
        self.LoadSearchDatas()

    def SetItem(self, item: ChristmasItem, rowData):
        account = rowData[1]
        member = self.GetMemberByAccount(account)
        if member == None:
            self.LogE(f"找不到成員：{account}")
            return
        item.id = int(rowData[0])
        item.member = member
        item.bless = rowData[2]
        item.message = rowData[3]

    def LoadItems(self):
        pass
        command = f"SELECT id, user, bless, message FROM festival_2023_christmas_item_{self.bot.bot.botSettings.sqlPostfix}"
        selectData = self.bot.bot.sql.SimpleSelect(command)
        allItems = []
        for rowData in selectData:
            item = ChristmasItem()
            self.SetItem(item, rowData)
            allItems.append(item)
        self.allItems = allItems
        self.LogI(f"聖誕節故事總數:{len(allItems)}")

    def LoadLogs(self):
        pass

    def LoadSearchDatas(self):
        # guild: discord.Guild = self.bot.bot.GetGuild()
        # guild.get_member_named()

        pass

    def GetMemberByAccount(self, account: str) -> discord.Member:
        member = self.bot.GetGuild().get_member_named(account)
        return member

    def GetRandomItem(self, onlyNever=True, skipUser=None) -> ChristmasItem:
        if len(self.allItems) <= 0:
            self.LogE("資料錯誤")
            return
        index = -1
        if onlyNever:
            size = len(self.allItems) - len(self.itemState)
            shift = random.randrange(size)
            for index in range(len(self.allItems)):
                if self.allItems[index].member in self.itemState:
                    pass
                else:
                    if shift == 0:
                        chooseIndex = index
                        break
                    else:
                        shift += -1
        else:
            chooseIndex = random.randrange(len(self.allItems))
        self.itemState[self.allItems[chooseIndex].member] = True
        return self.allItems[chooseIndex]

    def InsertDrawLog(self, item: ChristmasItem, drawUser: discord.Member):
        member = item.member
        command = (f"INSERT INTO festival_2023_christmas_log_{self.bot.bot.botSettings.sqlPostfix}"
                   "(user_id, user_name, draw_user_id, draw_user_name)"
                   "VALUES (%s, %s, %s, %s);")
        # command = (f"INSERT INTO festival_2023_christmas_log_{self.bot.bot.botSettings.sqlPostfix}"
        #            "(user_id, user_name, draw_user_id, draw_user_name, guess_user_id, guess_user_name)"
        #            "VALUES (%s, %s, %s, %s, %s, %s);")

        self.bot.bot.sql.SimpleCommand(
            command, (member.id, member.name, drawUser.id, drawUser.name))

    def UpdateGuessLog(self, drawUser: discord.Member):
        pass

    christmasGroup = SlashCommandGroup("聖誕節2023", "聖誕節的祝福指令")
    # christmasGroup = SlashCommandGroup("測試群組1212", "測試用的群組說明文字")

    @christmasGroup.command(name="抽取故事", description="抽出故事")
    # @christmasGroup.command(name="測試指令01", description="測試指令1的說明")
    async def draw(self, ctx: discord.ApplicationContext):
        pass
        if ctx.user.id not in TEST_USER_LIST:
            self.LogI(f"{ctx.user.display_name}({ctx.user.name}) 使用指令 draw")
            ctx.respond("非測試人員請勿使用", ephemeral=True)
            pass
        if ctx.user.id in self.allLogsByDrawId:
            msg = "你已經抽過了故事，抽到的故事："
            item = self.allLogsByDrawId[ctx.user.id]
        else:
            msg = "抽到的故事："
            item = self.GetRandomItem(onlyNever=False)
            self.InsertDrawLog(item=item, drawUser=ctx.user)

        await ctx.respond(msg)
        await ctx.respond(f"{item.message}")
        await ctx.respond(f"接下來請使用指令猜測故事的主人")

    @christmasGroup.command(name="猜測", description="故事的主人")
    # @christmasGroup.command(name="測試指令02",description="測試指令2的說明")
    async def guess(self, ctx: discord.ApplicationContext, member: discord.Member):
        if ctx.user.id not in TEST_USER_LIST:
            self.LogI(f"{ctx.user.display_name}({ctx.user.name}) 使用指令 guess")
            ctx.respond("非測試人員請勿使用", ephemeral=True)

        await ctx.respond("測試指令02")
        pass


def setup(bot):
    bot.add_cog(CogChristmas2023(bot))
