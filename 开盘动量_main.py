import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xlwt 
from 开盘动量 import opendriven
#from 开盘动量 import opendriven_cost
from 开盘动量 import opendriven_stop
from 开盘动量 import opendriven_stop_night
#from 开盘动量_evaluation import figure
from 开盘动量_evaluation import evaluation

if __name__ == '__main__':
    #获取数据
    df = pd.read_excel('IF.xlsx')
    date = []
    for i in range(len(df['date1'])):
        date.append(df['date1'][i].strftime("%Y/%m/%d"))

    df['date'] = date 
    
    
    df_list = [group[1] for group in df.groupby(df.date)]
    
    #设置参数
    begin = 45
    interval = 15
    flag = [0]*len(df_list)
    position = [0]*len(df_list)
    df_data = pd.concat([pd.DataFrame({'flag':flag}),pd.DataFrame({'position':position})],axis=1)


    #运行策略

    df_data_1,pd_transactions_1,stats_1 = opendriven(begin,interval,df_list,df_data)
    #df_data_2,pd_transactions_2,stats_2 = opendriven_stop(begin,interval,df_list,df_data)
    #df_data_3,pd_transactions_3,stats_3 = opendriven_stop_night(begin,interval,df_list,df_data)
    #df_data_4,pd_transactions_4,stats_4 = opendriven_cost(begin,interval,df_list,df_data)
    
    #策略对比图--画对比图，放在这里直接画比较方便，没用evaluation里的函数
    xtick = np.round(np.linspace(0, df_data_1.shape[0] - 1, 10), 0)
    xticklabel = df_data_1.date[xtick]
    plt.figure(figsize=(15,6.5))
    ax1 = plt.axes()
    # np.arange：返回一个有终点和起点的固定步长的序列，只有一个参数时代表终点，起点默认为0，步长为1
    plt.plot(np.arange(df_data_1.shape[0]), df_data_1.benchmark, 'yellow', label = 'Benchmark', linewidth = 2)
    #plt.plot(np.arange(df_data_1.shape[0]), df_data_1.nav, 'red', label = 'Opendriven', linewidth = 2)
    #plt.plot(np.arange(df_data_2.shape[0]), df_data_2.nav, 'blue', label = 'Opendriven_stop', linewidth = 2)
    #plt.plot(np.arange(df_data_4.shape[0]), df_data_4.nav, 'lightred', label = 'Opendriven_cost', linewidth = 2)
    plt.plot(np.arange(df_data_3.shape[0]), df_data_3.nav, 'green', label = 'Opendriven_stop_night', linewidth = 2)

    #plt.plot(np.arange(res5.shape[0]), res5.nav, 'red', label = 'RSRS_right_price', linewidth = 2)
    
    

    plt.legend()
    ax1.set_xticks(xtick)
    
    ax1.set_xticklabels(xticklabel,rotation = 45)# assign labels on x tick positions
    plt.savefig('return_opendriven.jpg')
    
    
    
    #年化收益
    #result1 = evaluation(trans5,res5)
    
    
    
