import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from evaluation import evaluation,evaluation_stoploss

#简单的动量策略
def simple_momentum(IF):
    data = IF.copy()
    raw_data = IF.copy()

    data['flag'] = 0 # 买卖标记
    data['position'] = 0 # 持仓标记，持仓：1，不持仓：0

    record_buy = [] #记录多头
    record_sell = [] #记录空头
    len_days = data.shape[0] - 240  #最后一天的数据不完整，不进行判断

    #用i分割出每天,i是每天的起始
    for i in range(0,len_days,240):

        #多仓
        if data.loc[i+29,'open']>data.loc[i+14,'open']>data.loc[i,'open']\
            and data.loc[i+44,'close']>data.loc[i+29,'close']>data.loc[i+14,'close']\
            and min(data.loc[i+30:i+45,'low'])>min(data.loc[i+15:i+30,'low'])>min(data.loc[i:i+15,'low']):
            
            data.loc[i,'flag'] = 1 #在起始位置标注开仓
            data.loc[i+45:i+240,'position'] = 1
            date_in = data.loc[i,'Date']  #记录买入日期
            data.loc[i+45,'close'] = np.average(data['close'][i+45:i+50], weights=data['volume'][i+45:i+50])*(1+0.00013)
            price_in = data.loc[i+45,'close'] #记录买入价格
            data.loc[i+239,'close'] = data.loc[i+239,'close']*(1-0.00013)
            price_out = data.loc[i+239,'close'] #卖出价格
            day_return = round((price_out/price_in-1)*100,2) #收益率
            record_buy.append([date_in, price_in,price_out, day_return])  #将价格和收益以列表形式添加到多头记录

        #空仓
        elif data.loc[i+29,'open']<data.loc[i+14,'open']<data.loc[i,'open']\
            and data.loc[i+44,'close']<data.loc[i+29,'close']<data.loc[i+14,'close']\
            and max(data.loc[i+30:i+45,'high'])<max(data.loc[i+15:i+30,'high'])<max(data.loc[i:i+15,'high']):

            data.loc[i,'flag'] = -1
            data.loc[i+45:i+240,'position'] = -1
            date_in = data.loc[i,'Date']
            data.loc[i+45,'close'] = np.average(data['close'][i+45:i+50], weights=data['volume'][i+45:i+50])*(1-0.00013)
            price_out = data.loc[i+45,'close']
            data.loc[i+239,'close'] = data.loc[i+239,'close']*(1+0.00013)
            price_in = data.loc[i+239,'close']
            day_return = round((price_out/price_in-1)*100,2)
            record_sell.append([date_in, price_in, price_out, day_return])
        
        else:
            continue  

    #将列表转化为矩阵，并赋予列名
    pd_buy = pd.DataFrame(record_buy, columns = ['date_1','price_in_1','price_out_1','day_return_1'])
    pd_sell = pd.DataFrame(record_sell, columns = ['date_0','price_in_0','price_out_0','day_return_0'])
    pd_transactions = pd.concat([pd_buy, pd_sell], axis = 1)

    data['simple_return'] = data.close.pct_change(1).fillna(0)
    data['benchmark'] = raw_data.close/data.close[0]
    data['nav'] = (1+data.close.pct_change(1).fillna(0)*data.position).cumprod()

    stats = evaluation(pd_transactions, data)
    '''
    # Output into Excel
    with pd.ExcelWriter("simple_momentum.xlsx") as writer:
        data.to_excel(writer, sheet_name='data')
        pd_transactions.to_excel(writer, sheet_name='trade_record')
        stats.to_excel(writer, sheet_name='evaluations')
    '''
    return data,pd_transactions,stats


#-------------------------------------------------------------------
#简单动量策略隔夜仓
def simple_momentum_overnight(IF):
    data = IF.copy()
    raw_data = IF.copy()

    data['flag'] = 0 # 买卖标记
    data['position'] = 0 # 持仓标记，持仓：1，不持仓：0

    record_buy = [] #记录多头
    record_sell = [] #记录空头
    len_days = data.shape[0] - 240  #最后一天的数据不完整，不进行判断

    #用i分割出每天,i是每天的起始
    for i in range(0,len_days,240):

        #多仓
        if data.loc[i+29,'open']>data.loc[i+14,'open']>data.loc[i,'open']\
            and data.loc[i+44,'close']>data.loc[i+29,'close']>data.loc[i+14,'close']\
            and min(data.loc[i+30:i+45,'low'])>min(data.loc[i+15:i+30,'low'])>min(data.loc[i:i+15,'low']):
            
            data.loc[i,'flag'] = 1 #在起始位置标注开仓
            data.loc[i+45:i+240,'position'] = 1
            date_in = data.loc[i,'Date']  #记录买入日期
            data.loc[i+45,'close'] = np.average(data['close'][i+45:i+50], weights=data['volume'][i+45:i+50])*(1+0.00013)
            price_in = data.loc[i+45,'close'] #记录买入价格
            data.loc[i+239,'close'] = data.loc[i+240,'open']*(1-0.00013)
            price_out = data.loc[i+239,'close'] #卖出价格
            day_return = round((price_out/price_in-1)*100,2) #收益率
            record_buy.append([date_in, price_in,price_out, day_return])  #将价格和收益以列表形式添加到多头记录

        #空仓
        elif data.loc[i+29,'open']<data.loc[i+14,'open']<data.loc[i,'open']\
            and data.loc[i+44,'close']<data.loc[i+29,'close']<data.loc[i+14,'close']\
            and max(data.loc[i+30:i+45,'high'])<max(data.loc[i+15:i+30,'high'])<max(data.loc[i:i+15,'high']):

            data.loc[i,'flag'] = -1
            data.loc[i+45:i+240,'position'] = -1
            date_in = data.loc[i,'Date']
            data.loc[i+45,'close'] = np.average(data['close'][i+45:i+50], weights=data['volume'][i+45:i+50])*(1-0.00013)
            price_out = data.loc[i+45,'close']
            data.loc[i+239,'close'] = data.loc[i+239,'close']*(1+0.00013)
            price_in = data.loc[i+239,'close']
            day_return = round((price_out/price_in-1)*100,2)
            record_sell.append([date_in, price_in, price_out, day_return])
        
        else:
            continue  

    #将列表转化为矩阵，并赋予列名
    pd_buy = pd.DataFrame(record_buy, columns = ['date_1','price_in_1','price_out_1','day_return_1'])
    pd_sell = pd.DataFrame(record_sell, columns = ['date_0','price_in_0','price_out_0','day_return_0'])
    pd_transactions = pd.concat([pd_buy, pd_sell], axis = 1)

    data['simple_return'] = data.close.pct_change(1).fillna(0)
    data['benchmark'] = raw_data.close/data.close[0]
    data['nav'] = (1+data.close.pct_change(1).fillna(0)*data.position).cumprod()

    stats = evaluation(pd_transactions, data)
    '''
    # Output into Excel
    with pd.ExcelWriter("simple_momentum_overnight_1.xlsx") as writer:
        data.to_excel(writer, sheet_name='data')
        pd_transactions.to_excel(writer, sheet_name='trade_record')
        stats.to_excel(writer, sheet_name='evaluations')
    '''
    return data,pd_transactions,stats


#-------------------------------------------------------------------
#加入止损信号的策略
def momentum_stoploss(IF):
    data = IF.copy()
    raw_data = IF.copy()

    data['flag'] = 0 # 买卖标记
    data['position'] = 0 # 持仓标记，持仓：1，不持仓：0
    data['signal1'] = 0 # 反向信号初始为零，出现反向信号标记1
    data['TR'] = 0 #计算每15分钟的TR
    data['ATR'] = 0 #计算每15分钟的ATR
    data['signal2'] = 0 #ATR反转信号
    data['total_sig'] = 0 #记录总计反转信号次数
    data['cut'] = 0 #记录减仓数量
    data['cut_price'] = 0 #记录减仓价格

    record_buy = [] #记录多头
    record_sell = [] #记录空头
    len_days = data.shape[0] - 240

    #用i分割出每天,i是每天的起始
    for i in range(0,len_days,240):

        #多仓
        if data.loc[i+29,'open']>data.loc[i+14,'open']>data.loc[i,'open']\
            and data.loc[i+44,'close']>data.loc[i+29,'close']>data.loc[i+14,'close']\
            and min(data.loc[i+30:i+45,'low'])>min(data.loc[i+15:i+30,'low'])>min(data.loc[i:i+15,'low']):
            
            data.loc[i,'flag'] = 1 #在起始位置标注开仓
            data.loc[i+45:i+240,'position'] = 1
            date_in = data.loc[i,'Date']  #记录买入日期
            data.loc[i+45,'close'] = np.average(data['close'][i+45:i+50], weights=data['volume'][i+45:i+50])*(1+0.00013)
            price_in = data.loc[i+45,'close'] #记录买入价格
            data.loc[i+239,'close'] = data.loc[i+239,'close']*(1-0.00013)
            price_out = data.loc[i+239,'close'] #卖出价格

            #反向信号，符合多仓买入后才执行
            for j in range(i+45,i+165,15):  #保证最后有5个K线可以比较
                if max(data.loc[j:j+15,'high'])>max(data.loc[j+15:j+30,'high'])>max(data.loc[j+30:j+45,'high'])>\
                   max(data.loc[j+45:j+60,'high'])>max(data.loc[j+60:j+75,'high']): #连续五个最高价递减
                   data.loc[j+75,'signal1'] = 1 #下个K线初始标记反向信号
            signal1_num = sum(data.loc[i:i+240,'signal1'])

            #ATR止损信号
            opt_high = max(data.loc[i:i+15,'high'])>max(data.loc[i+15:i+30,'high'])>max(data.loc[i+30:i+45,'high']) #将前三个最高价的最大值设定为初始
            for m in range(i,i+225,15):  #用m划分每天的15分钟,是每个K线的起点
                if max(data.loc[m:m+15,'high'])>opt_high:
                    opt_high = max(data.loc[m:m+15,'high']) #当前最优价格
                data.loc[m:m+15,'TR'] = max(max(data.loc[m:m+15,'high'])-min(data.loc[m:m+15,'low']),\
                    abs(max(data.loc[m:m+15,'high'])-data.loc[m-1,'close']),abs(min(data.loc[m:m+15,'low'])-data.loc[m-1,'close']))
                data.loc[m:m+15,'ATR'] = data.loc[1:m+15,'TR'].mean()
                if m>31 and data.loc[m+14,'close']<opt_high-2.5*data.loc[m+14,'ATR']: #从第四根K线之后开始判断
                    data.loc[m+15,'signal2'] = 1 #在下一根K线的起点标记
            signal2_num = sum(data.loc[i+45:i+240,'signal2'])

            #根据反向信号减仓
            data.loc[i:i+240,'total_sig'] = (data.loc[i:i+240,'signal1']+data.loc[i:i+240,'signal2']).cumsum()
            for m in range(i,i+225,15):
                if data.loc[m,'total_sig'] == 1:
                    data.loc[m:i+240,'position'] = 2/3
                    data.loc[m,'cut'] = 1/3
                    cut_price = np.average(data['close'][m:m+5], weights=data['volume'][m:m+5])*(1+0.00013)
                    data.loc[m,'cut_price'] = cut_price
                elif data.loc[m,'total_sig'] == 2:
                    data.loc[m:i+240,'position'] = 1/3
                    data.loc[m,'cut'] = 1/3  #每次减掉三分之一，但是存在一次就达到2的情况
                    cut_price = np.average(data['close'][m:m+5], weights=data['volume'][m:m+5])*(1+0.00013)
                    data.loc[m,'cut_price'] = cut_price
                elif data.loc[m,'total_sig'] >= 3:
                    data.loc[m:i+240,'position'] = 0
                    data.loc[m,'cut'] = 1/3
                    cut_price = np.average(data['close'][m:m+5], weights=data['volume'][m:m+5])*(1+0.00013)
                    data.loc[m,'cut_price'] = cut_price
                else:
                    continue

            day_return = round(((data.loc[i+239,'close']*data.loc[i+239,'position']+ \
                sum(np.multiply(np.array(data.loc[i:i+240,'cut']),np.array(data.loc[i:i+240,'cut_price']))))/data.loc[i+45,'close']-1)*100,2) #收益率：卖出总价格除以买入价格
            record_buy.append([date_in, price_in,price_out, day_return, signal1_num, signal2_num])  #将价格、收益、多仓反转记录以列表形式添加到多头记录


        #空仓
        elif data.loc[i+29,'open']<data.loc[i+14,'open']<data.loc[i,'open']\
            and data.loc[i+44,'close']<data.loc[i+29,'close']<data.loc[i+14,'close']\
            and max(data.loc[i+30:i+45,'high'])<max(data.loc[i+15:i+30,'high'])<max(data.loc[i:i+15,'high']):

            data.loc[i,'flag'] = -1
            data.loc[i+45:i+240,'position'] = -1
            date_in = data.loc[i,'Date']
            data.loc[i+45,'close'] = np.average(data['close'][i+46:i+51], weights=data['volume'][i+46:i+51])*(1-0.00013)
            price_out = data.loc[i+45,'close']
            data.loc[i+239,'close'] = data.loc[i+239,'close']*(1+0.00013)
            price_in = data.loc[i+239,'close']

            #反向信号
            for j in range(i+45,i+195,15):   #j是每天第四根15分钟K线及之后的起始，保证最后有三根K线可以比较
                if min(data.loc[j:j+15,'low'],default=0)<min(data.loc[j+15:i+30,'low'],default=0)<min(data.loc[j+30:j+45,'low'],default=0): #连续三个最低价递增
                   data.loc[j+45,'signal1'] = 1 #下个K线初始标记反向信号
            signal1_num = sum(data.loc[i:i+240,'signal1'])

            #ATR止损信号
            opt_low = min(data.loc[i:i+15,'low'])>max(data.loc[i+15:i+30,'low'])>max(data.loc[i+30:i+45,'low']) #将前三个最低价的最小值设定为初始
            for m in range(i,i+225,15):  #用m划分每天的15分钟,是每个K线的起点
                if min(data.loc[m:m+15,'low'])>opt_low:
                    opt_low = min(data.loc[m:m+15,'low']) #当前最优价格
                data.loc[m:m+15,'TR'] = max(max(data.loc[m:m+15,'high'])-min(data.loc[m:m+15,'low']),\
                    abs(max(data.loc[m:m+15,'high'])-data.loc[m-1,'close']),abs(min(data.loc[m:m+15,'low'])-data.loc[m-1,'close']))
                data.loc[m:m+15,'ATR'] = data.loc[1:m+15,'TR'].mean()
                if m>31 and data.loc[m+14,'close']>opt_low-2*data.loc[m+14,'ATR']: #从第四根K线之后开始判断
                    data.loc[m+15,'signal2'] = 1 #在下一根K线的起点标记
            signal2_num = sum(data.loc[i+45:i+240,'signal2'])

            #根据反向信号减仓
            data.loc[i:i+240,'total_sig'] = (data.loc[i:i+240,'signal1']+data.loc[i:i+240,'signal2']).cumsum()
            for m in range(i,i+225,15):
                if data.loc[m,'total_sig'] == 1:
                    data.loc[m:i+240,'position'] = -2/3
                    data.loc[m,'cut'] = 1/3
                    cut_price = np.average(data['close'][m:m+5], weights=data['volume'][m:m+5])*(1+0.00013)
                    data.loc[m,'cut_price'] = cut_price
                elif data.loc[m,'total_sig'] == 2:
                    data.loc[m:i+240,'position'] = -1/3
                    data.loc[m,'cut'] = 1/3  #每次减掉三分之一，但是存在一次就达到2的情况
                    cut_price = np.average(data['close'][m:m+5], weights=data['volume'][m:m+5])*(1+0.00013)
                    data.loc[m,'cut_price'] = cut_price
                elif data.loc[m,'total_sig'] >= 3:
                    data.loc[m:i+240,'position'] = 0
                    data.loc[m,'cut'] = 1/3
                    cut_price = np.average(data['close'][m:m+5], weights=data['volume'][m:m+5])*(1+0.00013)
                    data.loc[m,'cut_price'] = cut_price
                else:
                    continue

            day_return = round((price_out/(price_in*abs(data.loc[i+239,'position'])+\
                sum(data.loc[i:i+240,'cut']*data.loc[i:i+240,'cut_price']))-1)*100,2) #收益率：卖出总价格除以买入价格
            record_sell.append([date_in, price_in,price_out, day_return, signal1_num, signal2_num])  #将价格、收益、多仓反转记录以列表形式添加到多头记录

        else:
            continue

    #将列表转化为矩阵，并赋予列名
    pd_buy = pd.DataFrame(record_buy, columns = ['date_1','price_in_1','price_out_1','day_return_1','signal1','signal2'])
    pd_sell = pd.DataFrame(record_sell, columns = ['date_0','price_in_0','price_out_0','day_return_0','signal1','signal2'])
    pd_transactions = pd.concat([pd_buy, pd_sell], axis = 1)

    data['simple_return'] = data.close.pct_change(1).fillna(0)
    data['benchmark'] = raw_data.close/data.close[0]
    data['nav'] = (1+data.close.pct_change(1).fillna(0)*data.position).cumprod()

    stats = evaluation(pd_transactions, data)
    
    # Output into Excel
    with pd.ExcelWriter("momentum_stoploss_1.xlsx") as writer:
        data.to_excel(writer, sheet_name='data')
        pd_transactions.to_excel(writer, sheet_name='trade_record')
        stats.to_excel(writer, sheet_name='evaluations')
    
    return data,pd_transactions,stats

#--------------------------------------------------------------------------
#止损策略加隔夜仓
def momentum_stoploss_overnight(IF):
    data = IF.copy()
    raw_data = IF.copy()

    data['flag'] = 0 # 买卖标记
    data['position'] = 0 # 持仓标记，持仓：1，不持仓：0
    data['signal1'] = 0 # 反向信号初始为零，出现反向信号标记1
    data['TR'] = 0 #计算每15分钟的TR
    data['ATR'] = 0 #计算每15分钟的ATR
    data['signal2'] = 0 #ATR反转信号
    data['total_sig'] = 0 #记录总计反转信号次数
    data['cut'] = 0 #记录减仓数量
    data['cut_price'] = 0 #记录减仓价格

    record_buy = [] #记录多头
    record_sell = [] #记录空头
    len_days = data.shape[0] - 240

    #用i分割出每天,i是每天的起始
    for i in range(0,len_days,240):

        #多仓
        if data.loc[i+29,'open']>data.loc[i+14,'open']>data.loc[i,'open']\
            and data.loc[i+44,'close']>data.loc[i+29,'close']>data.loc[i+14,'close']\
            and min(data.loc[i+30:i+45,'low'])>min(data.loc[i+15:i+30,'low'])>min(data.loc[i:i+15,'low']):
            
            data.loc[i,'flag'] = 1 #在起始位置标注开仓
            data.loc[i+45:i+240,'position'] = 1
            date_in = data.loc[i,'Date']  #记录买入日期
            data.loc[i+45,'close'] = np.average(data['close'][i+45:i+50], weights=data['volume'][i+45:i+50])*(1+0.00013)
            price_in = data.loc[i+45,'close'] #记录买入价格
            data.loc[i+239,'close'] = data.loc[i+240,'open']*(1-0.00013)
            price_out = data.loc[i+239,'close'] #隔夜仓的卖出价格是第二天的开盘

            #反向信号，符合多仓买入后才执行
            for j in range(i+45,i+165,15):  #保证最后有5个K线可以比较
                if max(data.loc[j:j+15,'high'])>max(data.loc[j+15:j+30,'high'])>max(data.loc[j+30:j+45,'high'])>\
                   max(data.loc[j+45:j+60,'high'])>max(data.loc[j+60:j+75,'high']): #连续五个最高价递减
                   data.loc[j+75,'signal1'] = 1 #下个K线初始标记反向信号
            signal1_num = sum(data.loc[i:i+240,'signal1'])

            #ATR止损信号
            opt_high = max(data.loc[i:i+15,'high'])>max(data.loc[i+15:i+30,'high'])>max(data.loc[i+30:i+45,'high']) #将前三个最高价的最大值设定为初始
            for m in range(i,i+225,15):  #用m划分每天的15分钟,是每个K线的起点
                if max(data.loc[m:m+15,'high'])>opt_high:
                    opt_high = max(data.loc[m:m+15,'high']) #当前最优价格
                data.loc[m:m+15,'TR'] = max(max(data.loc[m:m+15,'high'])-min(data.loc[m:m+15,'low']),\
                    abs(max(data.loc[m:m+15,'high'])-data.loc[m-1,'close']),abs(min(data.loc[m:m+15,'low'])-data.loc[m-1,'close']))
                data.loc[m:m+15,'ATR'] = data.loc[1:m+15,'TR'].mean()
                if m>31 and data.loc[m+14,'close']<opt_high-2.5*data.loc[m+14,'ATR']: #从第四根K线之后开始判断
                    data.loc[m+15,'signal2'] = 1 #在下一根K线的起点标记
            signal2_num = sum(data.loc[i+45:i+240,'signal2'])

            #根据反向信号减仓
            data.loc[i:i+240,'total_sig'] = (data.loc[i:i+240,'signal1']+data.loc[i:i+240,'signal2']).cumsum()
            for m in range(i,i+225,15):
                if data.loc[m,'total_sig'] == 1:
                    data.loc[m:i+240,'position'] = 2/3
                    data.loc[m,'cut'] = 1/3
                    cut_price = np.average(data['close'][m:m+5], weights=data['volume'][m:m+5])*(1+0.00013)
                    data.loc[m,'cut_price'] = cut_price
                elif data.loc[m,'total_sig'] == 2:
                    data.loc[m:i+240,'position'] = 1/3
                    data.loc[m,'cut'] = 1/3  #每次减掉三分之一，但是存在一次就达到2的情况
                    cut_price = np.average(data['close'][m:m+5], weights=data['volume'][m:m+5])*(1+0.00013)
                    data.loc[m,'cut_price'] = cut_price
                elif data.loc[m,'total_sig'] >= 3:
                    data.loc[m:i+240,'position'] = 0
                    data.loc[m,'cut'] = 1/3
                    cut_price = np.average(data['close'][m:m+5], weights=data['volume'][m:m+5])*(1+0.00013)
                    data.loc[m,'cut_price'] = cut_price
                else:
                    continue

            day_return = round(((price_out*data.loc[i+239,'position']+\
                sum(data.loc[i:i+240,'cut']*data.loc[i:i+240,'cut_price']))/price_in-1)*100,2) #收益率：卖出总价格除以买入价格
            record_buy.append([date_in, price_in,price_out, day_return, signal1_num, signal2_num])  #将价格、收益、多仓反转记录以列表形式添加到多头记录


        #空仓
        elif data.loc[i+29,'open']<data.loc[i+14,'open']<data.loc[i,'open']\
            and data.loc[i+44,'close']<data.loc[i+29,'close']<data.loc[i+14,'close']\
            and max(data.loc[i+30:i+45,'high'])<max(data.loc[i+15:i+30,'high'])<max(data.loc[i:i+15,'high']):

            data.loc[i,'flag'] = -1
            data.loc[i+45:i+240,'position'] = -1
            date_in = data.loc[i,'Date']
            data.loc[i+45,'close'] = np.average(data['close'][i+45:i+50], weights=data['volume'][i+45:i+50])*(1-0.00013)
            price_out = data.loc[i+45,'close']
            data.loc[i+239,'close'] = data.loc[i+239,'close']*(1+0.00013)
            price_in = data.loc[i+239,'close']

            #反向信号
            for j in range(i+45,i+195,15):   #j是每天第四根15分钟K线及之后的起始，保证最后有三根K线可以比较
                if min(data.loc[j:j+15,'low'],default=0)<min(data.loc[j+15:i+30,'low'],default=0)<min(data.loc[j+30:j+45,'low'],default=0): #连续三个最低价递增
                   data.loc[j+45,'signal1'] = 1 #下个K线初始标记反向信号
            signal1_num = sum(data.loc[i:i+240,'signal1'])

            #ATR止损信号
            opt_low = min(data.loc[i:i+15,'low'])>max(data.loc[i+15:i+30,'low'])>max(data.loc[i+30:i+45,'low']) #将前三个最低价的最小值设定为初始
            for m in range(i,i+225,15):  #用m划分每天的15分钟,是每个K线的起点
                if min(data.loc[m:m+15,'low'])>opt_low:
                    opt_low = min(data.loc[m:m+15,'low']) #当前最优价格
                data.loc[m:m+15,'TR'] = max(max(data.loc[m:m+15,'high'])-min(data.loc[m:m+15,'low']),\
                    abs(max(data.loc[m:m+15,'high'])-data.loc[m-1,'close']),abs(min(data.loc[m:m+15,'low'])-data.loc[m-1,'close']))
                data.loc[m:m+15,'ATR'] = data.loc[1:m+15,'TR'].mean()
                if m>31 and data.loc[m+14,'close']>opt_low-2*data.loc[m+14,'ATR']: #从第四根K线之后开始判断
                    data.loc[m+15,'signal2'] = 1 #在下一根K线的起点标记
            signal2_num = sum(data.loc[i+45:i+240,'signal2'])

            #根据反向信号减仓
            data.loc[i:i+240,'total_sig'] = (data.loc[i:i+240,'signal1']+data.loc[i:i+240,'signal2']).cumsum()
            for m in range(i,i+225,15):
                if data.loc[m,'total_sig'] == 1:
                    data.loc[m:i+240,'position'] = -2/3
                    data.loc[m,'cut'] = 1/3
                    cut_price = np.average(data['close'][m:m+5], weights=data['volume'][m:m+5])*(1+0.00013)
                    data.loc[m,'cut_price'] = cut_price
                elif data.loc[m,'total_sig'] == 2:
                    data.loc[m:i+240,'position'] = -1/3
                    data.loc[m,'cut'] = 1/3  #每次减掉三分之一，但是存在一次就达到2的情况
                    cut_price = np.average(data['close'][m:m+5], weights=data['volume'][m:m+5])*(1+0.00013)
                    data.loc[m,'cut_price'] = cut_price
                elif data.loc[m,'total_sig'] >= 3:
                    data.loc[m:i+240,'position'] = 0
                    data.loc[m,'cut'] = 1/3
                    cut_price = np.average(data['close'][m:m+5], weights=data['volume'][m:m+5])*(1+0.00013)
                    data.loc[m,'cut_price'] = cut_price
                else:
                    continue

            day_return = round((price_out/(price_in*abs(data.loc[i+239,'position'])+\
                sum(data.loc[i:i+240,'cut']*data.loc[i:i+240,'cut_price']))-1)*100,2) #收益率：卖出总价格除以买入价格
            record_sell.append([date_in, price_in,price_out, day_return, signal1_num, signal2_num])  #将价格、收益、多仓反转记录以列表形式添加到多头记录  

        else:
            continue

    #将列表转化为矩阵，并赋予列名
    pd_buy = pd.DataFrame(record_buy, columns = ['date_1','price_in_1','price_out_1','day_return_1','signal1','signal2'])
    pd_sell = pd.DataFrame(record_sell, columns = ['date_0','price_in_0','price_out_0','day_return_0','signal1','signal2'])
    pd_transactions = pd.concat([pd_buy, pd_sell], axis = 1)

    data['simple_return'] = data.close.pct_change(1).fillna(0)
    data['benchmark'] = raw_data.close/data.close[0]
    data['nav'] = (1+data.close.pct_change(1).fillna(0)*data.position).cumprod()

    stats = evaluation(pd_transactions, data)
    
    # Output into Excel
    with pd.ExcelWriter("momentum_overnight_1.xlsx") as writer:
        data.to_excel(writer, sheet_name='data')
        pd_transactions.to_excel(writer, sheet_name='trade_record')
        stats.to_excel(writer, sheet_name='evaluations')
    
    return data,pd_transactions,stats