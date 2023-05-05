"""
创建和读取 orderbook 数据
"""
import pandas as pd
from datetime import datetime


class OrderBook():
    def __init__(self, data, symbol='IF2206') -> None:
        self.orderbook = data

    def get_price_volume(self, datetime, direction, trade_volume):
        # prefix = direction.title() + 'Price'
        # prices = ['a', prefix + '02', prefix + '03', prefix + '04', prefix + '05']
        # prefix = direction.title() + 'Volume'
        # volumes = [prefix + '01', prefix + '02', prefix + '03', prefix + '04', prefix + '05']
        buy_prices = ['a1', 'a2', 'a3', 'a4', 'a5']
        buy_volumes = ['a1_v', 'a2_v', 'a3_v', 'a4_v', 'a5_v']
        sell_prices = ['b1', 'b2', 'b3', 'b4', 'b5']
        sell_volumes = ['b1_v', 'b2_v', 'b3_v', 'b4_v', 'b5_v']

        trade_detail = {}
        current_vol = 0
        i = 0
        while current_vol < trade_volume and i <= 4:
            if direction == 'buy':
                volume = self.orderbook.get(datetime).get(buy_volumes[i])
                price = self.orderbook.get(datetime).get(buy_prices[i])
                this_trade_vol = min(volume, trade_volume - current_vol)
                # 交易的 量、价 详情
                trade_detail[i] = {'price': price, 'volume': this_trade_vol}
                current_vol += this_trade_vol
                i += 1
            elif direction == 'sell':
                volume = self.orderbook.get(datetime).get(sell_volumes[i])
                price = self.orderbook.get(datetime).get(sell_prices[i])
                this_trade_vol = min(volume, trade_volume - current_vol)
                # 交易的 量、价 详情
                trade_detail[i] = {'price': price, 'volume': this_trade_vol}
                current_vol += this_trade_vol
                i += 1
            else:
                raise ValueError(f"please enter correct direction: buy or sell")

        if current_vol < trade_volume:
            raise ValueError(
                f"Cannot {direction} {trade_volume} unit at {datetime}! Please trade less than {current_vol} unit.")
        return trade_detail

    def get_mid_price(self, datetime):
        bid = self.orderbook.get(datetime).get('a1')
        ask = self.orderbook.get(datetime).get('b1')
        return (bid + ask) / 2



def get_orderbook_data(date):
    path = r'/Users/wuqian/Desktop/project_group1/data/tick_stock.csv'
    data = pd.read_csv(path)
    data = data.set_index('datetime')
    data.index = pd.to_datetime(data.index)
    # 只需要五档的价格和volume
    # 获得那一天的order book
    day_data = data[data.index.date == date]
    day_data = day_data[['a1', 'a2', 'a3', 'a4', 'a5',
                 'b1', 'b2', 'b3', 'b4', 'b5',
                 'a1_v', 'a2_v', 'a3_v', 'a4_v', 'a5_v',
                 'b1_v', 'b2_v', 'b3_v', 'b4_v', 'b5_v']]
    day_data = day_data.resample('1T').first()
    time_list = list(day_data.index)
    data_dict = day_data.to_dict('index')
    return data_dict, time_list


if __name__ == '__main__':
    # 获得分钟频的订单簿
    data = pd.read_csv('/Users/wuqian/Desktop/project_group1/data/tick_stock.csv')
    data = data.set_index('datetime')
    data.index = pd.to_datetime(data.index)
    print('get tick stock!')

    # 获得分钟频的订单簿
    min_data = data[['a1', 'a2', 'a3', 'a4', 'a5',
                     'b1', 'b2', 'b3', 'b4', 'b5',
                     'a1_v', 'a2_v', 'a3_v', 'a4_v', 'a5_v',
                     'b1_v', 'b2_v', 'b3_v', 'b4_v', 'b5_v']]
    min_data = min_data.resample('1T').first()
    print('get minute tick data!')

    invest_cash = 1000000
    trade_data = pd.read_csv('/Users/wuqian/Desktop/project_group1/data/daily_df_beta.csv')
    real_trade_data = trade_data[trade_data['flag'] != 0]
    real_trade_datelist = real_trade_data['date'].to_list() # 有交易的日期
    real_trade_data = real_trade_data.set_index('date')
    real_trade_price = real_trade_data['open'].to_dict()  # 获取交易价格序列
    real_trade_signal = real_trade_data['flag'].to_dict()  # 获取信号序列
    real_trade_number = real_trade_data['quantity'].to_dict()  # 获取成交量
    print('get trade signals!')

    for dt in real_trade_datelist:

        new_date = pd.to_datetime(dt)
        # date = dt.date()
        dt_orderbook = min_data.loc[min_data.index.date == new_date]
        dt_orderbook.dropna(how='any', inplace=True)
        data_dict = dt_orderbook.to_dict('index')
        time_list = list(dt_orderbook.index)
        ob = OrderBook(data_dict, symbol='IF2206')

        # signal = 'buy' if real_trade_signal[dt] == 1 else 'sell'

        for i in range(0,len(time_list)):

            ts = time_list[i]
            # datetime(2022, 1, 4, 9,37,55,9)
            # print(ts)

            # ts为交易时间
            # buy为交易方向
            # 最后那个数字输入你要买多少股
            if real_trade_signal[dt] == 1:
                price = ob.get_price_volume(ts, 'buy', 100)
            else:
                price = ob.get_price_volume(ts, 'sell', 100)
            print(price) # 会输出你在这个时间，以什么价格，成功买了多少股
