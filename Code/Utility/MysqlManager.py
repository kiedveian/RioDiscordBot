import pymysql


class MysqlManager:
    _conn = None
    cursor = None
    db_settings = {}

    def __init__(self, host, port, user_name, password, schema_name, charset="utf8mb4") -> None:
        self.ChangeSetting(host=host, port=port, user_name=user_name,
                           password=password, schema_name=schema_name, charset=charset)
        self._CreateConnection(self.db_settings)

    def ChangeSetting(self, host, port, user_name, password, schema_name, charset="utf8mb4"):
        self.db_settings = {
            "host": host,
            "port": port,
            "user": user_name,
            "password": password,
            "db": schema_name,
            "charset": charset
        }

    def GetConnection(self):
        if self._conn == None:
            self._CreateConnection()
        self._conn.ping()
        return self._conn

    def SimpleSelect(self, command, *args, **kwargs):
        conn = self.GetConnection()
        with conn.cursor() as cursor:
            try:
                cursor.execute(command, *args, **kwargs)
                result = cursor.fetchall()
                return result
            except pymysql.Error as e:
                print("command error pymysql %d: %s" % (e.args[0], e.args[1]))
        return None

    def SimpleCommand(self, command, *args, **kwargs):
        conn = self.GetConnection()
        with conn.cursor() as cursor:
            try:
                cursor.execute(command, *args, **kwargs)
                conn.commit()
            except pymysql.Error as e:
                print("command error pymysql %d: %s" % (e.args[0], e.args[1]))
                conn.rollback()

    def _CreateConnection(self, db_settings):
        try:
            self._conn = pymysql.connect(**db_settings)
        except Exception as ex:
            print("create connection error")
            print(ex)

    def SimpleCommandMany(self, command, *args, **kwargs):
        conn = self.GetConnection()
        with conn.cursor() as cursor:
            try:
                cursor.executemany(command, *args, **kwargs)
                conn.commit()
            except pymysql.Error as e:
                print("command error pymysql %d: %s" % (e.args[0], e.args[1]))
                conn.rollback()
