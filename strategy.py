# 引入常用库
import pandas as pd
import numpy as np
import statsmodels.api as sm
# import scipy.stats as st
import datetime as dt
import itertools # 迭代器工具
import talib # 技术分析
import math
# 画图
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import seaborn as sns
from pylab import *
import matplotlib
# 设置字体 用来正常显示中文标签
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei']
# 用来正常显示负号
plt.rcParams['axes.unicode_minus'] = False
# 图表主题
plt.style.use('ggplot')
# 忽略报错
import warnings
warnings.filterwarnings("ignore")

def cal_statistics(df):
    # 净值序列
    df['net_asset_pct_chg'] = df.net_asset_value.pct_change(1).fillna(0)

    # 总收益率和年化收益率
    total_ret = df['net_asset_value'].iloc[-1]-1
    annual_ret = total_ret**(1/(df.shape[0]/252))-1
    total_ret = total_ret*100
    annual_ret = annual_ret*100

    # 夏普比率
    sharp_ratio = df['net_asset_pct_chg'].mean() * math.sqrt(252)/df['net_asset_pct_chg'].std()

    # 回撤
    df['high_level'] = df['net_asset_value'].rolling(min_periods = 1, window = len(df),center = False).max()
    df['draw_down'] = df['net_asset_value'] - df['high_level']
    df['draw_down_pct'] = df['draw_down'] / df['high_level'] * 100
    max_draw_down = df['draw_down'].min()
    max_draw_down_pct = df['draw_down_pct'].min()

    # 持仓总天数
    hold_days = df['position'].sum()

    # 交易次数
    trade_count = df[df['flag']!=0].shape[0]/2

    # 平均持仓天数
    avg_hold_days = int(hold_days/trade_count)

    # 获利天数
    profit_days = df[df['net_asset_pct_chg']>0].shape[0]
    # 亏损天数
    loss_days = df[df['net_asset_pct_chg']<0].shape[0]

    # 胜率（按天）
    winrate_day = profit_days/(profit_days+loss_days)*100
    # 平均盈利率（按天）
    avg_profit_rate_day = df[df['net_asset_pct_chg']>0]['net_asset_pct_chg'].mean()*100
    # 平均亏损率（按天）
    avg_loss_rate_day = df[df['net_asset_pct_chg']<0]['net_asset_pct_chg'].mean()*100
    # 平均盈亏比（按天）
    avg_pl_ratio_day = avg_profit_rate_day/ abs(avg_loss_rate_day)

    # 每次交易情况
    buy_trades = df[df['flag']==1].reset_index()
    sell_trades = df[df['flag']==-1].reset_index()
    result_trade = {
        'buy':buy_trades['close'],
        'sell':sell_trades['close'],
        'pct_chg':(sell_trades['close'] - buy_trades['close'])/buy_trades['close']
    }
    result_trade = pd.DataFrame(result_trade)

    # 盈利次数
    profit_trades = result_trade[result_trade['pct_chg']>0].shape[0]
    # 亏损次数
    loss_trades = result_trade[result_trade['pct_chg']<0].shape[0]
    # 单次最大盈利
    max_profit_trade = result_trade['pct_chg'].max()*100
    # 单次最大亏损
    max_loss_trade = result_trade['pct_chg'].min()*100
    # 胜率（按次）
    winrate_trade = profit_trades/(profit_trades+loss_trades)*100
    # 平均盈利率（按次）
    avg_profit_rate_trade = result_trade[result_trade['pct_chg']>0]['pct_chg'].mean()*100
    # 平均亏损率（按次）
    avg_loss_rate_trade = result_trade[result_trade['pct_chg']<0]['pct_chg'].mean()*100
    # 平均盈亏比（按次）
    avg_pl_ratio_trade = avg_profit_rate_trade/ abs(avg_loss_rate_trade)

    statistics_result = {
        'net_asset_value':df['net_asset_value'].iloc[-1],#最终净值
        'total_return':total_ret,#收益率
        'annual_return':annual_ret,#年化收益率
        'sharp_ratio':sharp_ratio,#夏普比率
        'max_draw_percent':max_draw_down_pct,#最大回撤
        'hold_days':hold_days,#持仓天数
        'trade_count':trade_count,#交易次数
        'avg_hold_days':avg_hold_days,#平均持仓天数
        'profit_days':profit_days,#盈利天数
        'loss_days':loss_days,#亏损天数
        'winrate_by_day':winrate_day,#胜率（按天）
        'avg_profit_rate_day':avg_profit_rate_day,#平均盈利率（按天）
        'avg_loss_rate_day':avg_loss_rate_day,#平均亏损率（按天）
        'avg_profit_loss_ratio_day':avg_pl_ratio_day,#平均盈亏比（按天）
        'profit_trades':profit_trades,#盈利次数
        'loss_trades':loss_trades,#亏损次数
        'max_profit_trade':max_profit_trade,#单次最大盈利
        'max_loss_trade':max_loss_trade,#单次最大亏损
        'winrate_by_trade':winrate_trade,#胜率（按次）
        'avg_profit_rate_trade':avg_profit_rate_trade,#平均盈利率（按次）
        'avg_loss_rate_trade':avg_loss_rate_trade,#平均亏损率（按次）
        'avg_profit_loss_ratio_trade':avg_pl_ratio_trade#平均盈亏比（按次）
    }

    return statistics_result


# 策略
def stratege(df1: pd.DataFrame, colname: str, buy_threshold: int, sell_threshold: int):
    # 初始资金
    money = 1000000
    # 买入股数
    num = 0
    # 手续费
    cost = 0.001
    # 是否持有（0:未持有）
    position = 0

    for i in range(len(df1.index) - 1):
        if df1[colname].iloc[i] > buy_threshold and position == 0:
            buy_price = df1['open'].iloc[i]
            # buy_time = df1['date'].iloc[i]
            num = (money // buy_price // 100) * 100
            money -= num * buy_price * (1 + cost)
            if money > 0:
                df1['flag'].iloc[i] = 1  # 开仓
                df1['position'].iloc[i + 1] = 1  # 下一个仓位不空
                position = 1
                df1['quantity'].iloc[i] = num
                # 账户余额变化
            else:
                money += num * buy_price * (1 + cost)
                df1['quantity'].iloc[i] = 0
                position = 0
                df1['flag'].iloc[i] = 0  # 开仓
                df1['position'].iloc[i + 1] = 0  # 下一个仓位不空
        elif df1[colname].iloc[i] < sell_threshold and position == 1:
            df1['flag'].iloc[i] = -1  # 平仓
            df1['position'].iloc[i + 1] = 0  # 空仓
            position = 0
            # 账户余额变化
            sell_price = df1['open'].iloc[i]
            # sell_time = df1['date'].iloc[i]
            # num = (money // sell_price // 100) * 100
            money += num * sell_price * (1 - cost)
            df1['num'].iloc[i] = -num
        elif position == 1 and df1['open'].iloc[i] < 0.8 * buy_price:  # 止损
            df1['flag'].iloc[i] = -1  # 平仓
            df1['position'].iloc[i + 1] = 0  # 空仓
            position = 0
            # 账户余额变化
            sell_price = df1['open'].iloc[i]
            # sell_time = df1['date'].iloc[i]
            # num = (money // sell_price // 100) * 100
            money += num * sell_price * (1 - cost)
            df1['num'].iloc[i] = -num
        else:
            df1['position'].iloc[i + 1] = df1['position'].iloc[i]
            df1['num'].iloc[i] = 0

        if position == 1:
            df1['asset_value'].iloc[i] = money + df1['close'].iloc[i] * num
        elif position == 0:
            df1['asset_value'].iloc[i] = money
        print(money)


    # 计算净值序列
    df1['net_asset_value'] = (1 + df1.close.pct_change(1).fillna(0) * df1.position).cumprod()
    df1['asset_value'].iloc[-1] = df1['asset_value'].iloc[-2]

    return df1

# 11111斜率方法：用连续N日的最高价与最低价的线性回归模型的斜率来量化支撑位与阻力位的相对强度（RSRS）

# 构建斜率指标：
# Step 1: 取前 N 日(N=18)的最高价序列与最低价序列。
# Step 2: 将两列数据进行 OLS 线性回归。
# Step 3: 将拟合后的 beta 值作为当日 RSRS 斜率指标值。

# 策略：
# 1. 计算 RSRS 斜率。
# 2. 如果斜率大于 1，则买入持有。
# 3. 如果斜率小于 0.8，则卖出手中持股平仓。

def cal_beta(df,n):

    nbeta = []
    trade_days = len(df.index)
    df['position'] = 0
    df['flag'] = 0
    df['num'] = 0
    position = 0

    for i in range(trade_days):
        if i < (n-1):
            continue
        else:
            x = df['low'].iloc[i-n+1:i+1]
            x = sm.add_constant(x)
            y = df['high'].iloc[i-n+1:i+1]
            model = sm.OLS(y,x)
            res = model.fit()
            beta = round(res.params[1],2)
            nbeta.append(beta)
    df1 = df.iloc[n-1:]
    df1['beta'] = nbeta
    df1['asset_value'] = 0

    # 策略：
    df1 = stratege(df1,'beta',0.9, 0.8)

    return df1

# 数据
stock = pd.read_csv('/Users/wuqian/Desktop/project_group1/data/min_stock.csv')
stock['datetime'] = pd.to_datetime(stock['datetime'])
stock.set_index('datetime',inplace = True)
stock = stock[['high','low','close','open','volume']]

n = 18
df_beta = cal_beta(stock,n)
df_beta.to_csv('/Users/wuqian/Desktop/project_group1/data/df_beta.csv')

# statistics
# statistic_beta = pd.DataFrame(cal_statistics(df_beta),index=['斜率方法']).T


