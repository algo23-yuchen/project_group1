import pandas as pd
from pymysql import *


# 云数据库基本信息
host='rm-cn-wwo379zrv000loko.rwlb.rds.aliyuncs.com'
port=3306
user='algo23'
passwd="MFEpro66"
db='project'

#数据库连接
conn = connect(host=host,port=port,user=user,passwd=passwd,db=db,charset='utf8')
#游标对象
cursor = conn.cursor()

#往已建表格里插入数据
data = pd.read_csv(r'D:\CUHK\23Term2\MFE 5210\Project\marketdata\601318_daily_price.csv')


for i in list(range(data.shape[0])):
    sql = "INSERT INTO Daily_data VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(data.iloc[i,0],data.iloc[i,1],data.iloc[i,2],data.iloc[i,3],data.iloc[i,4],data.iloc[i,5],data.iloc[i,6],data.iloc[i,7],data.iloc[i,8],data.iloc[i,9],data.iloc[i,10],data.iloc[i,11])
    cursor.execute(sql)
    conn.commit()


data = pd.read_csv(r'D:\CUHK\23Term2\MFE 5210\Project\marketdata\601318_tick_price.csv')
for i in list(range(data.shape[0])):
    sql = "INSERT INTO Tick_data VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(data.iloc[i,0],data.iloc[i,1],data.iloc[i,2],data.iloc[i,3],data.iloc[i,4],data.iloc[i,5],data.iloc[i,6],data.iloc[i,7],data.iloc[i,8],data.iloc[i,9],data.iloc[i,10],data.iloc[i,11],data.iloc[i,12],data.iloc[i,13],data.iloc[i,14],data.iloc[i,15],data.iloc[i,16],data.iloc[i,17],data.iloc[i,18],data.iloc[i,19],data.iloc[i,20],data.iloc[i,21],data.iloc[i,22],data.iloc[i,23],data.iloc[i,24],data.iloc[i,25],data.iloc[i,26],data.iloc[i,27],data.iloc[i,28],data.iloc[i,29],data.iloc[i,30],data.iloc[i,31],data.iloc[i,32])
    cursor.execute(sql)
    conn.commit()

#关闭连接
conn.close()