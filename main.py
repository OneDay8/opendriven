import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from timing_strategy import simple_momentum,simple_momentum_overnight,momentum_stoploss,momentum_stoploss_overnight
from evaluation import figure

if __name__ == '__main__':
    IF = pd.read_csv('IF.csv',encoding='utf-8')
    #data1,trans1,stats1 = simple_momentum(IF)
    #data2,trans2,stats2 = simple_momentum_overnight(IF)
    data3,trans3,stats3 = momentum_stoploss(IF)
    #data4,trans4,stats4 = momentum_stoploss_overnight(IF)

    print(stats3)
    #print(stats2)
    #print(stats3)
    #print(stats4)
    figure(data3)

    '''
    #策略对比图
    data = data1.copy()
    xtick = np.round(np.linspace(0, data.shape[0] - 1, 10), 0)
    xticklabel = data.Date[xtick]
    plt.figure(figsize=(15,6.5))
    ax1 = plt.axes()
    # np.arange：返回一个有终点和起点的固定步长的序列，只有一个参数时代表终点，起点默认为0，步长为1
    plt.plot(np.arange(data1.shape[0]), data.benchmark, 'yellow', label = 'Benchmark', linewidth = 2)
    plt.plot(np.arange(data1.shape[0]), data1.nav, 'purple', label = 'simple_momentum', linewidth = 2)
    plt.plot(np.arange(data2.shape[0]), data2.nav, 'blue', label = 'simple_momentum_overnight', linewidth = 2)
    plt.plot(np.arange(data3.shape[0]), data3.nav, 'green', label = 'momentum_stoploss', linewidth = 2)
    plt.plot(np.arange(data4.shape[0]), data4.nav, 'red', label = 'momentum_stoploss_overnight', linewidth = 2)

    plt.legend()
    ax1.set_xticks(xtick)
    ax1.set_xticklabels(xticklabel,rotation = 45)# assign labels on x tick positions
    plt.savefig('return of all.jpg')
    '''