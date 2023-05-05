from MySQLOperation import MySQLOperation
from pymysql import *

# 云数据库基本信息
host='rm-cn-wwo379zrv000loko.rwlb.rds.aliyuncs.com'
port=3306
user='algo23'
passwd="MFEpro66"
db='project'


# 方法实例化
MySQL = MySQLOperation(host, port, db, user, passwd)

# 建表
sql_CreateMarketDailyData = '''CREATE TABLE Daily_data (
                        order_book_id CHAR(20),
                        trading_date date,
                        total_turnover float,
                        low decimal(9,5),
                        open decimal(9,5),
                        volume float,
                        high decimal(9,5),
                        limit_down decimal(9,5),
                        limit_up decimal(9,5),
                        num_trade float,
                        close decimal(9,5),
                        prev_close decimal(9,5));'''

MySQL.Execute_Code(sql_CreateMarketDailyData)

sql_CreateMarketTickData = '''CREATE TABLE Tick_data (
                        order_book_id CHAR(20),
                        TradingTime datetime,
                        trading_date date,
                        open decimal(9,3),
                        last decimal(9,3),
                        high decimal(9,3),
                        low decimal(9,3),
                        prev_close decimal(9,3),
                        volume float,
                        total_turnover float,
                        limit_up decimal(9,3),
                        limit_down decimal(9,3),
                        SellPrice01 decimal(9,3),
                        SellPrice02 decimal(9,3),
                        SellPrice03 decimal(9,3),
                        SellPrice04 decimal(9,3),
                        SellPrice05 decimal(9,3),
                        BuyPrice01 decimal(9,3),
                        BuyPrice02 decimal(9,3),
                        BuyPrice03 decimal(9,3),
                        BuyPrice04 decimal(9,3),
                        BuyPrice05 decimal(9,3),
                        SellVolume01 int,
                        SellVolume02 int,
                        SellVolume03 int,
                        SellVolume04 int,
                        SellVolume05 int,
                        BuyVolume01 int,
                        BuyVolume02 int,
                        BuyVolume03 int,
                        BuyVolume04 int,
                        BuyVolume05 int,
                        change_rate decimal(11,6))'''
MySQL.Execute_Code(sql_CreateMarketTickData)
