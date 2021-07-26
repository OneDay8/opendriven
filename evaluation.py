import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def evaluation(trans,data):
    N= 60000

    #Annual simple return
    ret_y = data.nav[data.shape[0] - 1]**(N / data.shape[0]) - 1

    #Annual Sharpe Ratio
    #Sharpe_ratio = (((data.simple_return * data.position).mean())-0.000082)/ \
                   #(data.simple_return * data.position).std() * np.sqrt(250)
    
    Sharpe_ratio = (((data.simple_return * data.position)-0.00000084).mean())/ \
                   (data.simple_return * data.position).std() * np.sqrt(60000)

    # Get drawdown and maximum drawdown
    drawdown = 1 - data.nav / data.nav.cummax()  #cummax()：给出序列前N个的最大值，由此可以计算出每个时点的回撤
    max_drawdown = max(drawdown)  #取回撤序列的最大值

    #trading times
    num = data.flag.abs().sum()

    # win rate
    positive_num = 0
    for i in trans.day_return_1:
        if i > 0:
            positive_num = positive_num+1
        else:
            continue 
    for j in trans.day_return_0:
        if j > 0:
            positive_num = positive_num+1
        else:
            continue 
    win_ratio = round(positive_num/num*100,2)
    
    #win_ratio = round(((trans.day_return_1> 0)+(trans.day_return_0> 0))/num*100,2)

    result = {'Sharp': Sharpe_ratio,
              'Ret_y': ret_y,
              'Win_rate': win_ratio,
              'MDD': max_drawdown,
              'Trading_times': num}
    
    result = pd.DataFrame.from_dict(result, orient='index').T  #字典转为矩阵

    return result

def evaluation_stoploss(trans,data):
    N= 60000

    #Annual simple return
    ret_y = data.nav[data.shape[0] - 1]**(N / data.shape[0]) - 1

    #Annual Sharpe Ratio
    #Sharpe_ratio = (((data.simple_return * data.position).mean())-0.00004926)/ \
                   #(data.simple_return * data.position).std() * np.sqrt(60000)
    
    Sharpe_ratio = (((data.simple_return * data.position).mean())-0.00000006)/ \
                   (data.simple_return * data.position).std() * np.sqrt(60000)

    # Get drawdown and maximum drawdown
    drawdown = 1 - data.nav / data.nav.cummax()  #cummax()：给出序列前N个的最大值，由此可以计算出每个时点的回撤
    max_drawdown = max(drawdown)  #取回撤序列的最大值

    #trading times
    num = data.flag.abs().sum()

    # win rate
    positive_num = 0
    for i in trans.day_return_1:
        if i > 0:
            positive_num = positive_num+1
        else:
            continue 
    for j in trans.day_return_0:
        if j > 0:
            positive_num = positive_num+1
        else:
            continue 
    win_ratio = round(positive_num/num*100,2)
    
    #win_ratio = round(((trans.day_return_1> 0)+(trans.day_return_0> 0))/num*100,2)

    result = {'Sharp': Sharpe_ratio,
              'Ret_y': ret_y,
              'Win_rate': win_ratio,
              'MDD': max_drawdown,
              'Trading_times': num}
    
    result = pd.DataFrame.from_dict(result, orient='index').T  #字典转为矩阵

    return result

#绘制净值曲线
def figure(result):
    data = result.copy()
    xtick = np.round(np.linspace(0, data.shape[0] - 1, 10), 0)
    xticklabel = data.Date[xtick]
    plt.figure(figsize=(15,6.5))
    ax1 = plt.axes()
    # np.arange：返回一个有终点和起点的固定步长的序列，只有一个参数时代表终点，起点默认为0，步长为1
    plt.plot(np.arange(data.shape[0]), data.benchmark, 'yellow', label = 'Benchmark', linewidth = 2)
    plt.plot(np.arange(data.shape[0]), data.nav, 'purple', label = 'momentum_stoploss_overnight', linewidth = 2)
    plt.legend()
    ax1.set_xticks(xtick)
    ax1.set_xticklabels(xticklabel,rotation = 45)# assign labels on x tick positions
    plt.savefig('momentum_stoploss_overnight.jpg')

    return
