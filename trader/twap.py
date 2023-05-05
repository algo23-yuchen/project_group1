from time import time
import pandas as pd
import numpy as np
import datetime
from OrderBook import OrderBook, get_orderbook_data

class Twap():
    """
    Twap 算法计算了在一天可交易的时间段内完成设定的下单手数。
    """
    #def __init__(self, symbol='IF2206', account=None, cash_start, position_value_start, signal_date, per_volumn, position_start,signal):
    def __init__(self, cash_start, position_value_start, signal_date, per_trade_volumn, position_start,signal,trade_num,time_list,orderbook_data, symbol='IF2206', account=None):
        """创建 Twap 实例
            code (string): 拟下单的合约代码,
            account: [可选]指定发送下单指令的账户实例, 多账户模式下，该参数必须指定
            cash_start：当天初始现金价值
            position_value_start：当天初始持仓价值
            signal_date: 交易信号所在日期
            per_volumn：当天每次交易数量
            position_start：当天初始仓位
            signal：当天交易信号（-1，1），只输入仓位有变化的日期
            trade_num:当天交易次数
        """
        self._account = account
        self._symbol = symbol
        self.signal_date= None

        #twap 交易的参数
        self.trade_num = trade_num
        self.per_volumn = per_trade_volumn

        # orderbook 数据 
        #orderbook_data,time_list=get_orderbook_data(r'orderbook.csv')
        self.time_list = time_list
        self.orderbook = OrderBook(data=orderbook_data, symbol=symbol)  # TODO 从数据库获取数据

        self.trade_info = {}  # 所有的 trade 信息数据
        
        # 参数
        self.cash_daily = cash_start # 初始化现金账户为上期现金值
        self.position_value_daily = position_value_start
        self.commission = 0.001  
        self.all_value_daily = None
        self.position_daily = position_start
        self.signal = signal
    '''
    def set_span_and_per_volume(self, span:int, per_volume:int):
        """ 设置 twap 的交易参数
            span (int): 算法执行交易的总时长，以秒为单位
            per_volume (int):  每次下单的手数
        """
        self.span = span
        self.per_volumn = per_volumn
    '''
    
    def get_trade_ts(self, start_time):
        """获取每次交易的时间，以分钟为单位
            start_time (datetime): 本次交易开始时间点
            返回当天twap拆单的所有交易时间点
        """
        trade_time = []
        for i in range(self.trade_num):
            end_time = start_time + datetime.timedelta(minutes=240 // self.trade_num) #
            time_inner = [t for t in self.time_list if end_time > t > start_time]
            start_time = end_time
            trade_time.append(time_inner[0]) 
        return trade_time

    def buy(self, timestamp, position):#本次下单数量
        #买端看卖方订单簿
        price_vol = self.orderbook.get_price_volume(datetime=timestamp, 
                                    direction='sell', trade_volume=position)
        price_vol_data= pd.DataFrame.from_dict(price_vol) 
        
        self.position_daily += position
        long_position_value=np.sum(price_vol_data.loc['price_sell'] * price_vol_data.loc['volume'])
        self.position_value_daily += long_position_value
        self.cost = self.commission * long_position_value
        self.cash_daily = self.cash_daily - self.cost - self.position_value_daily #理想情况下slef.cash=0，全部买入，实际不一定
        self.all_value_daily = self.cash_daily + self.position_value_daily

        avg_price =  self.position_value_daily / position
        
        trade_info = {'direction':'buy', 'avg_price':avg_price, 'volume':position, 'trade_detail':price_vol}
        return trade_info

    def sell(self, timestamp, position):#TOMODIFY
        #卖端看买方订单簿        
        price_vol = self.orderbook.get_price_volume(datetime=timestamp, 
                                    direction='buy', trade_volume=position)
        price_vol_data = pd.DataFrame.from_dict(price_vol) 

        # 更新持仓数据
        self.position_daily -= position
        #assert self.position >= 0, 'cannot have negative position!'
        short_position_value=np.sum(price_vol_data.loc['price_buy'] * price_vol_data.loc['volume'])
        self.position_value_daily -= short_position_value #更新持仓价值，理想情况全部卖出，self.position_value=0
        
        self.cost = self.commission * abs(short_position_value)
        self.cash_daily = self.cash_daily- short_position_value - self.cost
        self.all_value_daily = self.cash_daily + self.position_value_daily
        
        avg_price =  self.position_value_daily / position

        trade_info = {'direction':'sell', 'avg_price':avg_price, 'volume':position, 'trade_detail':price_vol}
        return trade_info
        
    def trade(self, start_time):
        """
        进行交易
        ---direction (str): 交易方向，'buy' or 'sell'
        ---total_volume (int): 下单的总手数
        ---start_time (datetime): 本次交易开始时间点

        返回dict: 交易信息
        """
        trade_time = self.get_trade_ts(start_time)
        if self.signal > 0:
            for t in trade_time:
                self.trade_info[t] = self.buy(t,self.per_volumn)
                self.trade_info[t]['position_value'] = self.position_value_daily

        elif self.signal < 0:
            for t in trade_time:
                self.trade_info[t] = self.sell(t,self.per_volumn)
                self.trade_info[t]['position_value'] = self.position_value_daily

        return self.trade_info
    
if __name__ == '__main__':
    # 导入每周数据
    inputdata=pd.read_csv('trade_results.csv')
    inputdata=inputdata.rename(columns={inputdata.columns[0]:'datetime'}) #修改列名
    inputdata['datetime']=pd.to_datetime(inputdata['datetime'])
    inputdata=inputdata.set_index('datetime')
    
    #需输入的参数cash_start, position_value_start, signal_date, per_volumn, position_start,signal,trade_num
    param_data=inputdata[inputdata['signal']!=0]
    cash_start_list=param_data['cash'].to_dict()
    position_value_start_list=param_data['position_value'].to_dict()
    signal_date_list=param_data.index.to_list()
    position_start_list=param_data['position'].to_dict()
    signal_list=param_data['signal'].to_dict()

    #数据库更新后需改正
    data = pd.read_csv('orderbook.csv')
    data = data.set_index('datetime')
    data.index = pd.to_datetime(data.index)

    # 获得五分钟频的订单簿
    min_data = data[['a1', 'a2', 'a3', 'a4', 'a5',
                     'b1', 'b2', 'b3', 'b4', 'b5',
                     'a1_v', 'a2_v', 'a3_v', 'a4_v', 'a5_v',
                     'b1_v', 'b2_v', 'b3_v', 'b4_v', 'b5_v']]
    
    min_data = min_data.resample('5T').first()
    time_list = list(min_data.index)

    orderbook_data = min_data.to_dict('index')
    
    #其他需指定的参数
    trade_num=5
    param_data['per_volumn']=param_data['position']//trade_num
    start_time=datetime.datetime.strptime('2018-03-23 9:00:00','%Y-%m-%d %H:%M:%S') 
    per_volumn_list=param_data['per_volumn'].to_dict()
    
    trade_dict = {}
    #price = 0 # TODO 就是 bid ask price
    # 调用 twap 类，进行模拟交易 
    for dt in signal_date_list:
        twap=Twap(cash_start_list[dt],position_value_start_list[dt],dt,per_volumn_list[dt],position_start_list[dt],signal_list[dt],trade_num,time_list,orderbook_data)
        trade_dict[dt] = twap.trade(start_time)
    
    #trade_data = pd.DataFrame.from_dict(trade_dict, 'index')  # 获得交易持仓净值数据
    #trade_data.index = pd.to_datetime(trade_data.index)
