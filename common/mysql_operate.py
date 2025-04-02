"""
封装数据库的增改查方法
"""
# 导入处理数据库的包
import pymysql
# 老样子，导入获取yaml的方法来读取数据库配置信息
from common.yaml_config import GetConfig


class MysqlOperate:
    # 初始化数据库，把数据库字段映射上
    def __init__(self):
        # 获取到yaml里的数据库配置信息
        mysql_config = GetConfig().get_mysql_config()
        # 把获取的值一一对应上
        self.host = mysql_config['host']
        self.db = mysql_config['db']
        self.port = mysql_config['port']
        self.user = mysql_config['user']
        self.password = mysql_config['password']
        self.conn = None
        self.cursor = None

    # 数据库建立连接
    def __conn_db(self):
        # 用到try，因为有时候会出现数据库连接失败的情况，
        try:
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                port=self.port,
                charset='utf8'
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(e)
            return False
        return True

    # 关闭数据库连接，随手关门养成好习惯
    def __close_conn(self):
        self.cursor.close()
        self.conn.close()
        return True

    # 增、改后要commit一下，提交到数据库
    def __commit(self):
        self.conn.commit()
        return True

    def query(self, sql):
        """
        查询数据库
        :param sql: sql查询语句
        :return:
        """
        # 建立连接
        self.__conn_db()
        # 操作数据库查询
        self.cursor.execute(sql)
        query_data = self.cur.fetchall()
        # 如果查询的是空，就返回None
        if query_data == ():
            query_data = None
            print("没有获取到数据")
        # 不是空就继续往下走
        else:
            pass
        # 关闭数据库连接
        self.__close_conn()
        # return出查询的接口
        return query_data

    def insert_update_table(self, sql):
        """
        插入数据或者修改数据
        :param sql: 增、改sql语句
        :return:
        """
        # 建立连接
        self.__conn_db()
        # 执行sql
        self.cur.execute(sql)
        # commit一下
        self.__commit()
        # 关闭数据库连接
        self.__close_conn()
        # return出查询的接口
        return True

# 导入 MysqlOperate 类
from mysql_operate import MysqlOperate

# 实例化 MysqlOperate 类
mysql_handler = MysqlOperate()

# 执行查询操作
query_sql = "SELECT * FROM monitor_asin_abnormal WHERE task_detail_type = 13"
query_result = mysql_handler.query(query_sql)

# 处理查询结果
if query_result:
    for row in query_result:
        # 处理每一行数据
        print(row)
else:
    print("没有获取到数据")
