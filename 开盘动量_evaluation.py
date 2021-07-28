import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from openpyxl import load_workbook
import xlwt 

def evaluation(pd_buy,pd_sell,data):
    N = 250

    # Annual simple return，data.shape[0]-1表示数据量，**表示幂运算
    ret_y = data.nav[data.shape[0] - 1]**(N / data.shape[0]) - 1
    
    # Sharpe Ratio：收益均值/标准差
  
    #Sharpe_ratio = (data.return_after * data.flag).mean() / (data.return_after * data.flag).std() * np.sqrt(N) #np.sqrt函数计算每个元素的开方
    Sharpe_ratio = (data.return_after_all * data.flag).mean() / (data.return_after_all * data.flag).std() * np.sqrt(N) #np.sqrt函数计算每个元素的开方
    
    # win rate，(trans.price_sell - trans.price_buy) > 0为真返回1，假返回0
  
    r_buy = len(pd_buy.price_buy)/(len(pd_buy.price_buy)+len(pd_sell.price_sell))
    r_sell = len(pd_sell.price_sell)/(len(pd_buy.price_buy)+len(pd_sell.price_sell))
    win_ratio = ((pd_buy.price_close_buy - pd_buy.price_buy) > 0).mean() * r_buy + (-(pd_sell.price_close_sell - pd_sell.price_sell) > 0).mean() * r_sell

    # Get drawdown and maximum drawdown
    drawdown = 1 - data.nav / data.nav.cummax()  #cummax()：给出序列前N个的最大值，由此可以计算出每个时点的回撤
    max_drawdown = max(drawdown)  #取回撤序列的最大值

    # get maximum loss rate

    max_loss = min(min(pd_buy.price_close_buy / pd_buy.price_buy - 1),-(max(pd_sell.price_close_sell / pd_sell.price_sell - 1)))  #发生损失时卖价小于买价，所以trans.price_sell/trans.price_buy-1<0

    #trading times
    num = data.flag.abs().sum()

    result = {'Sharp': Sharpe_ratio,
              'Ret_y': ret_y,
              'Win_rate': win_ratio,
              'MDD': max_drawdown,
              'Max_loss_rate': -max_loss,
              'Trading_times': num}
    result = pd.DataFrame.from_dict(result, orient='index').T  #字典转为矩阵

    return result
'''
    # Evaluation per year
    data['year'] = data.date.apply(lambda x: x[:4]) #lambda x: x[:4]表示参数为x，操作为切片
    nav_per_year = data.nav.groupby(data.year).last() / data.nav.groupby(data.year).first() - 1  #通过年份分组后，最后/最初-1得到每年的收益率
    benchmark_per_year = data.benchmark.groupby(data.year).last()/data.benchmark.groupby(data.year).first() - 1
    
    excess_ret = nav_per_year - benchmark_per_year  #计算每年的超额收益
    result_per_year = pd.concat([nav_per_year,benchmark_per_year,excess_ret], axis = 1)  #数据合并
    result_per_year.columns = ['Simple return','Benchmark return','Excess return']  #赋予列名
    result_per_year = result_per_year.T  #矩阵转置


#绘制净值曲线
def figure(result):
    data = result.copy()
    xtick = np.round(np.linspace(0, data.shape[0] - 1, 10), 0)
    xticklabel = data.date[xtick]
    plt.figure(figsize=(15,6.5))
    ax1 = plt.axes()
    # np.arange：返回一个有终点和起点的固定步长的序列，只有一个参数时代表终点，起点默认为0，步长为1
    plt.plot(np.arange(data.shape[0]), data.benchmark, 'yellow', label = 'Benchmark', linewidth = 2)
    plt.plot(np.arange(data.shape[0]), data.nav, 'purple', label = 'RSRS_right_volume_correlation', linewidth = 2)
    plt.legend()
    ax1.set_xticks(xtick)
    ax1.set_xticklabels(xticklabel,rotation = 45)# assign labels on x tick positions
    plt.savefig('return_right_vol.jpg')

    return
'''
