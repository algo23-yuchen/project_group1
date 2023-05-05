import datetime
from pymysql import *
from sqlalchemy import create_engine
import pandas as pd
from MySQLOperation import MySQLOperation


def DownloadData(table,stock,starttime,endtime,fieldstr,
                 host='rm-cn-wwo379zrv000loko.rwlb.rds.aliyuncs.com',port=3306,user='algo23',passwd="MFEpro66",db='project'):
    MySQL = MySQLOperation(host, port, db, user, passwd)
    sqlstr = "SELECT %s FROM %s WHERE order_book_id=%s AND  trading_date>='%s' AND trading_date <='%s' "%(fieldstr,table,stock,starttime,endtime)
    result = MySQL.Select_Code(sqlstr)
    data = pd.DataFrame(result)

    return data

table = 'tick_data'
stock = '601318'
start = datetime.date(2020,1,1)
end = datetime.date(2023,1,20)
fieldstr = 'trading_date,low,open,high,prev_close'
data = DownloadData(table,stock,start,end,fieldstr)
print(data)

# 记得改trading_date
# SQL语句需要字符串单引号，
# 如SELECT trading_date,low,open,high,prev_close FROM tick_data WHERE order_book_id=601318 AND  trading_date <='2020-01-05'AND trading_date>='2020-01-06'