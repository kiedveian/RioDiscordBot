import os
from django.shortcuts import render
from django.views.generic import TemplateView

from Utility.MysqlManager import MysqlManager


class HomePageView(TemplateView):
    template_name = "home.html"


class AbuotPageView(TemplateView):
    template_name = "about.html"


class Sticker1PageView(TemplateView):

    template_name = "sticker1.html"

    def get_datas(self):
        pass

        sql = MysqlManager(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user_name=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            schema_name=os.getenv("MYSQL_SCHEMA_NAME")
        )
        # command = f"SELECT user_id, draw_alarm_message FROM user_data_{self.botSettings.sqlPostfix} WHERE draw_alarm_message != 0"
        command = (f"SELECT COUNT(0) AS `count`, `stk`.`name`, `log`.`sticker_id`, `stk`.url"
                   f" FROM (`message_log_nerolirain` `log` JOIN `all_sticker` `stk` ON ((`log`.`sticker_id` = `stk`.`sticker_id`)))"
                   f" WHERE (`stk`.`guild_id` = 824892342455500800)"
                   f" GROUP BY `log`.`sticker_id` ORDER BY `count` DESC"
                   )
        result = sql.SimpleSelect(command)
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['sticker_datas'] = self.get_datas()
        # context['number'] = random.randrange(1, 100)
        return context
