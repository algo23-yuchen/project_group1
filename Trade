'''
根据因子信号signal进行交易
signal:0,1,-1
Volumn:每次需成交数量，有符号，正向为买入，负向为卖出

Functions 
- backtest 进行回测
    - 需要调用 Trade 类

Class
- Trade  根据策略信号 进行 买buy()、卖sell()、remain() 等操作
- - 有七个属性需要输出:'trade_price', 'signal', 'all_value', 'volumn', 'position_value', 'cash', 'cost'

Return
- trade_data [dict]  {date: {
                            'date','all_position_value', 'cash',
                            'value', 'signal', 'cost',
                            '','r_price','position', 'position_value'}
                     }
'''
import pandas as pd
import datetime


class Trade():
    def __init__(self, invest_cash=1000000):
        #申明参数
        self.signal_date = None  
        self.trade_price = None
        self.signal = None

        # 参数：初始资金 1
        self.investcash = invest_cash
        self.commission = 0.001

        # 交易数据
        self.cash = invest_cash  #初始化现金为上期现金值 
        self.volumn = 0 #初始化持有头寸，也为成交量，全部成交
        self.position_value = 0 #初始化持仓价值
        self.all_value = invest_cash #初始化资产价值

    def buy(self):
        long_position_value = self.volumn * self.trade_price #考虑佣金后，持仓价值与初始投资不同        
        self.cost = self.commission * long_position_value
        
        self.cash = 0 #所有现金转为0，全部买入标的
        self.position_value = self.cash + long_position_value #所有头寸今天的价值
        self.all_value=self.cash+self.position_value

    def sell(self): 
        short_position_value = self.volumn * self.trade_price # 将卖出的头寸价值，为负数

        self.cost = self.commission * abs(short_position_value)
        self.cash = self.cash - short_position_value - self.cost #头寸全部卖出
        
        self.volumn = 0 #所有头寸全部卖出
        self.position_value = 0
        self.all_value = self.cash + self.position_value

    def remain(self):
        self.get_position_value()
        self.value = self.cash + self.position_value

    def get_position_value(self):
        self.position_value = self.volumn * self.trade_price

    def signalcoming(self, date, price, signal):
        self.signal_date = date
        self.trade_price = price  
        self.signal = signal

    def trade(self):
        """ 开始交易"""
        if self.signal > 0:
            if self.cash > self.trade_price: #需有足够资金才能买入
                self.buy()
        elif self.signal < 0:  
            if self.position > 0:  #持有头寸才能生效       
                self.sell()
        elif self.signal == 0:
            self.remain()
        else:
            raise ValueError('Invalid "signal" value!')
            
        self.value = self.position_value + self.cash   
        trade_info = self.get_trade_data()
        
        self.show_trading_info()  # 打印交易详情
        
        return trade_info

    # 获取并存储交易价格，交易信号，资产价值，成交量，头寸价值，现金账户和成本7个参数数据
    def get_trade_data(self):
        parameter_list = ['trade_price', 'signal', 'all_value', 'volumn', 'position_value', 'cash', 'cost']
        value_list = {name: getattr(self, name) for name in param_list}
        return value_list

    def show_trading_info(self):
        if self.signal > 0:
            print(f'{self.date_time} 买入，'
                  f'持仓价值 {self.position_value:.2f}，现价价值 {self.cash:.2f} ')
        elif self.signal < 0:
            print(f'{self.date_time} 卖出，'
                  f'持仓价值 {self.position_value:.2f}，现金价值 {self.cash:.2f} ')
        else:
            print(f'{self.date_time} 无操作，当前持仓价值 {self.position_value:.2f}，总资产价值 {self.value:.2f}')




if __name__ == '__main__':
    
    #导入策略输出数据
    trade_data = pd.read_csv(r'data\202202data.csv', index_col=2)#将时间作为index
    trade_data.index = pd.to_datetime(trade_data.index)
    
    trade_datelist = trade_data.index.to_list()
    trade_price = trade_data['OpenPrice'].to_dict() #获取交易价格序列
    trade_signal=trade_data['signal'].to_dict() #获取信号序列

    trade_dict = {}
    # 调用 Trade 类，进行模拟交易
    trade = Trade()  
    for date in trade_dattlist:
        trade.signalcoming(date, price=trade_price[date], signal=trade_signal[date])
        trade_dict[date] = trade.trade()
    
    trade_data = pd.DataFrame.from_dict(trade_dict, 'index')  # 获得交易持仓净值数据
    trade_data.index = pd.to_datetime(trade_data.index)
    trade_data.to_csv('result/trade_data.csv')
