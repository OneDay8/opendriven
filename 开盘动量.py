import pandas as pd
import datetime
import numpy as np 
import statsmodels.formula.api as sml
import matplotlib.pyplot as plt
import scipy.stats as scs
import matplotlib.mlab as mlab
from openpyxl import load_workbook
from 开盘动量_evaluation import evaluation
import tushare as ts
import time

def getdata(dateStart,dateEnd,N,M):
    HS300 = ts.get_k_data('000300', index=True,start = '{}'.format(dateStart),end = '{}'.format(dateEnd))
    HS300=HS300[['date','high','low','open','close']]
    return HS300








'''
#计算相关系数\
def cor(begin,df_list):
    return_begin = []
    return_after = []
    for day in range(len(df_list)):
        return_begin_1 = (df_list[day]['close'].iloc[begin-1]-df_list[day]['open'].iloc[0])/df_list[day]['open'].iloc[0]
        return_after_1 = (df_list[day]['close'].iloc[len(df_list[day]['close'])-1]-df_list[day]['open'].iloc[begin])/df_list[day]['open'].iloc[begin]
        return_begin.append(return_begin_1)
        return_after.append(return_after_1)
    return_begin = pd.Series(return_begin)
    return_after = pd.Series(return_after)
    cor_1 = return_begin.corr(return_after)
    return cor_1,return_begin,return_after

correlation = []
return_after_a_mean = []
return_after_b_mean = []
return_after_c_mean = []
return_after_d_mean = []
return_after_e_mean = []
for begin in [15,30,45,60,75,90,105]:
    return_after_a = []
    return_after_b = []
    return_after_c = []
    return_after_d = []
    return_after_e = []
    cor_1,return_begin,return_after = cor(begin,df_list)
    correlation.append(cor_1)

    df['return_begin'] = return_begin
    df['return_after'] = return_after
    df['rank_begin'] = df['return_begin'].rank(method='first')
    
    
    for i in range(len(return_begin)):
        if 1 <= df['rank_begin'][i] <= len(return_begin)/5:
            return_after_a.append(df['return_after'][i])
        elif len(return_begin)/5 < df['rank_begin'][i] <= len(return_begin)/5*2:
            return_after_b.append(df['return_after'][i])
        elif len(return_begin)/5*2 < df['rank_begin'][i] <= len(return_begin)/5*3:
            return_after_c.append(df['return_after'][i])
        elif len(return_begin)/5*3 < df['rank_begin'][i] <= len(return_begin)/5*4:
            return_after_d.append(df['return_after'][i])
        else:
            return_after_e.append(df['return_after'][i])
    
    return_after_a_mean.append(np.mean(return_after_a))
    return_after_b_mean.append(np.mean(return_after_b))
    return_after_c_mean.append(np.mean(return_after_c))
    return_after_d_mean.append(np.mean(return_after_d))
    return_after_e_mean.append(np.mean(return_after_e))
'''
#开盘动量基础策略
def opendriven(begin,interval,df_list,df_data):
    data = df_list.copy()
    df_data['flag'] = 0 # 持仓标记，持多仓：1，不持仓：0，持空仓：-1
    record_buy = []
    record_sell = []
    
    return_begin = []
    return_after = []
    #return_after_cost = []
    return_date = []
    return_open = []
    return_close = []
    for day in range(len(data)):
        begin_open_price = np.average(data[day]['open'][0:5],weights = data[day]['vol'][0:5])
        begin_close_price = np.average(data[day]['close'][begin-5:begin],weights = data[day]['vol'][begin-5:begin])
        return_begin_1 = (begin_close_price*(1-0.00013)-begin_open_price*1.00013)/begin_open_price*1.00013
        #加上双边交易费1.3%%
        after_open_price = np.average(data[day]['open'][begin:begin+4],weights = data[day]['vol'][begin:begin+4])
        after_close_price = np.average(data[day]['close'][-5::],weights = data[day]['vol'][-5::])
        return_after_1 = (after_close_price*(1-0.00013) - after_open_price*1.00013) / after_open_price*1.00013
        return_begin.append(return_begin_1)
        return_after.append(return_after_1)
       
        return_date.append(data[day]['date'].iloc[0])
        return_open.append(data[day]['open'].iloc[0])
        return_close.append(data[day]['close'].iloc[-1])
     
        
        
        #开多仓
        if min(data[day]['low'][0:interval]) < min(data[day]['low'][interval:interval*2]) < min(data[day]['low'][interval*2:interval*3]) \
            and data[day]['close'].iloc[interval-1] < data[day]['close'].iloc[interval*2-1] < data[day]['close'].iloc[interval*3-1] \
                and data[day]['open'].iloc[0] < data[day]['open'].iloc[interval] < data[day]['open'].iloc[interval*2]:

            df_data.loc[day,'flag'] = 1
            date_in = data[day]['date'].iloc[0]  #记录买入日期
            
            # 出错
            #记录买入价格
            price_in = np.average(data[day]['close'][interval*3:interval*3+4],weights = data[day]['vol'][interval*3:interval*3+4])*1.00013
            price_close_buy = np.average(data[day]['close'][-5::],weights = data[day]['vol'][-5::])*(1-0.00013)
             #记录平仓价格
            record_buy.append([date_in, price_in,price_close_buy])  #将日期和价格以列表形式添加到买入记录
            
        #开空仓
        elif data[day]['close'].iloc[interval-1] > data[day]['close'].iloc[interval*2-1] > data[day]['close'].iloc[interval*3-1] \
            and max(data[day]['high'][0:interval]) > max(data[day]['high'][interval:interval*2]) > max(data[day]['high'][interval*2:interval*3]) \
                and data[day]['open'].iloc[0] > data[day]['open'].iloc[interval] > data[day]['open'].iloc[interval*2]:
            
        
            df_data.loc[day,'flag'] = -1
            date_out = data[day]['date'].iloc[0]  #记录卖出日期
            price_out = np.average(data[day]['close'][interval*3:interval*3+4],weights = data[day]['vol'][interval*3:interval*3+4])*1.00013
            #记录卖出价格
            price_close_sell = np.average(data[day]['close'][-5::],weights = data[day]['vol'][-5::])*(1-0.00013)  #记录平仓价格
            record_sell.append([date_out, price_out,price_close_sell])  #将日期和价格以列表形式添加到买入记录
        
        else:
            df_data.loc[day,'flag'] = 0

    df_data['date'] = return_date
    df_data['return_begin'] = return_begin
    df_data['return_after'] = return_after
    df_data['return_after_all'] = return_after
    df_data['open'] = return_open
    df_data['close'] = return_close

        
    #将列表转化为矩阵，并赋予列名
    pd_buy = pd.DataFrame(record_buy, columns = ['date_buy','price_buy','price_close_buy'])
    pd_sell = pd.DataFrame(record_sell, columns = ['date_sell','price_sell','price_close_sell'])
    pd_transactions = pd.concat([pd_buy, pd_sell], axis = 1)  #pd.concat：连接函数，将买卖记录整合为交易记录


    #data['simple_return'] = data.close.pct_change(1).fillna(0)
    df_data['nav'] = (1+df_data.return_after_all.fillna(0)*df_data.flag).cumprod()
    df_data['benchmark'] = df_data.close / df_data.close[0] #将CLOSE[0]的净值设定为1，计算基准净值
    
    
    stats = evaluation(pd_buy,pd_sell, df_data) #计算评价指标
    # Output into Excel
    with pd.ExcelWriter("开盘动量.xlsx") as writer:
        df_data.to_excel(writer, sheet_name='stock_data')
        pd_transactions.to_excel(writer, sheet_name='trade_record')
        stats.to_excel(writer, sheet_name='evaluations')

    return df_data,pd_transactions,stats

#加上止损和吊灯
def opendriven_stop(begin,interval,df_list,df_data):
    data = df_list.copy()
    df_data = df_data.iloc[0:-1]
    
    df_data['flag'] = 0 # 持仓标记，持多仓：1，不持仓：0，持空仓：-1
    record_buy = []
    record_sell = []
    
    return_begin = []
    return_after = []
    return_after_all = []
    return_date = []
    return_open = []
    return_close = []
    num_n = []
    for day in range(len(data)):
        begin_open_price = np.average(data[day]['open'][0:5],weights = data[day]['vol'][0:5])
        begin_close_price = np.average(data[day]['close'][begin-5:begin],weights = data[day]['vol'][begin-5:begin])
        return_begin_1 = (begin_close_price*(1-0.00013)-begin_open_price*1.00013)/begin_open_price*1.00013
        #加上双边交易费1.3%%
        after_open_price = np.average(data[day]['open'][begin:begin+4],weights = data[day]['vol'][begin:begin+4])
        after_close_price = np.average(data[day]['close'][-5::],weights = data[day]['vol'][-5::])
        return_after_1 = (after_close_price*(1-0.00013) - after_open_price*1.00013) / after_open_price*1.00013
        return_begin.append(return_begin_1)
        return_after.append(return_after_1)
       
        return_date.append(data[day]['date'].iloc[0])
        return_open.append(data[day]['open'].iloc[0])
        return_close.append(data[day]['close'].iloc[-1])
    
        
        
         #开多仓
        if min(data[day]['low'][0:interval]) < min(data[day]['low'][interval:interval*2]) < min(data[day]['low'][interval*2:interval*3]) \
            and data[day]['close'].iloc[interval-1] < data[day]['close'].iloc[interval*2-1] < data[day]['close'].iloc[interval*3-1] \
                and data[day]['open'].iloc[0] < data[day]['open'].iloc[interval] < data[day]['open'].iloc[interval*2]:

            df_data.loc[day,'flag'] = 1
            date_in = data[day]['date'].iloc[0]  #记录买入日期
            
           
            #记录买入价格
            price_in = np.average(data[day]['close'][interval*3:interval*3+4],weights = data[day]['vol'][interval*3:interval*3+4])*1.00013
           
            price_close_buy = np.average(data[day]['close'][-5::],weights = data[day]['vol'][-5::])*(1-0.00013)
             #记录平仓价格
            record_buy.append([date_in, price_in,price_close_buy])  #将日期和价格以列表形式添加到买入记录
           
            
            price_stop = [np.average(data[day]['close'][begin-5:begin], weights=data[day]['vol'][begin-5:begin])*(1-0.00013)]
            return_after_section = []
            
            n = 0
            TR = []
            for i in range(int(len(data[day]['high'])/interval-5)):
                #衰弱止损指标计算
                high_low = max(data[day]['high'][0:interval*(i+5)]) - min(data[day]['low'][0:interval*(i+5)])
                preclose_high = np.abs(data[day-1]['close'].iloc[-1] - max(data[day]['high'][0:interval*(i+5)]))
                preclose_low = np.abs(data[day-1]['close'].iloc[-1] - min(data[day]['low'][0:interval*(i+5)]))
                TR_1 = max(high_low,preclose_high,preclose_low)
                TR.append(TR_1)
                maxhigh = max(data[day]['high'][0:interval*(i+5)])
                ATR=np.sum(TR)/(i+1)


                #反向止损
                if max(data[day]['high'][interval*i:interval*(i+1)]) >= max(data[day]['high'][interval*(i+1):interval*(i+2)]) \
                >= max(data[day]['high'][interval*(i+2):interval*(i+3)]) >= max(data[day]['high'][interval*(i+3):interval*(i+4)]) \
                >= max(data[day]['high'][interval*(i+4):interval*(i+5)]):
                                
                            price_stop_1 = np.average(data[day]['close'][interval*(i+5):interval*(i+5)+4], weights=data[day]['vol'][interval*(i+5):interval*(i+5)+4])*(1-0.00013)
                            price_stop.append(price_stop_1)
                                
                            return_after_section.append((price_stop[-1] - price_stop[-2])*((3-n)/3)/price_stop[-2])
                            n = n+1
                if n == 3:
                    break
                if (maxhigh - data[day]['low'].iloc[interval*(i+5)-1]) > ATR*2.5:
                            price_stop_2 = np.average(data[day]['close'][interval*(i+5):interval*(i+5)+4], weights=data[day]['vol'][interval*(i+5):interval*(i+5)+4])*(1-0.00013)
                            price_stop.append(price_stop_2)
                                    
                            return_after_section.append((price_stop[-1] - price_stop[-2])*((3-n)/3)/price_stop[-2])
                            n = n+1
                                    
                if n == 3:
                    break
                                
            
            price_stop_0 = np.average(data[day]['close'][-5::], weights=data[day]['vol'][-5::])*(1-0.00013)
            return_after_section.append((price_stop_0 - price_stop[-1])*((3-n)/3)/price_stop[-1])
            
            return_after_all_1 = sum(return_after_section)
            return_after_all.append(return_after_all_1)
            num_n.append(n)
        #开空仓
        elif data[day]['close'].iloc[interval-1] > data[day]['close'].iloc[interval*2-1] > data[day]['close'].iloc[interval*3-1] \
            and max(data[day]['high'][0:interval]) > max(data[day]['high'][interval:interval*2]) > max(data[day]['high'][interval*2:interval*3]) \
                and data[day]['open'].iloc[0] > data[day]['open'].iloc[interval] > data[day]['open'].iloc[interval*2]:
            
        
            df_data.loc[day,'flag'] = -1
            date_out = data[day]['date'].iloc[0]  #记录卖出日期
            price_out = np.average(data[day]['close'][interval*3:interval*3+4],weights = data[day]['vol'][interval*3:interval*3+4])*(1-0.00013)
            #记录卖出价格
            price_close_sell = np.average(data[day]['close'][-5::],weights = data[day]['vol'][-5::])*(1+0.00013)  #记录平仓价格
            record_sell.append([date_out, price_out,price_close_sell])  #将日期和价格以列表形式添加到买入记录
            n = 0
            TR = []
            price_stop = [np.average(data[day]['close'][begin-5:begin], weights=data[day]['vol'][begin-5:begin])*(1-0.00013)]
            return_after_section = []
            for i in range(int(len(data[day]['high'])/interval-3)):
                high_low = max(data[day]['high'][0:interval*(i+3)]) - min(data[day]['low'][0:interval*(i+3)])
                preclose_high = np.abs(data[day-1]['close'].iloc[-1] - max(data[day]['high'][0:interval*(i+3)]))
                preclose_low = np.abs(data[day-1]['close'].iloc[-1] - min(data[day]['low'][0:interval*(i+3)]))
                TR_1 = max(high_low,preclose_high,preclose_low)
                TR.append(TR_1)
                minlow = min(data[day]['low'][0:interval*(i+3)])
                ATR=np.sum(TR)/(i+1)

                #反向止损
                if min(data[day]['low'][interval*i:interval*(i+1)]) <= min(data[day]['low'][interval*(i+1):interval*(i+2)]) \
                    and min(data[day]['low'][interval*(i+1):interval*(i+2)]) <= min(data[day]['low'][interval*(i+2):interval*(i+3)]):
                        price_stop_1 = np.average(data[day]['close'][interval*(i+3):interval*(i+3)+4], weights=data[day]['vol'][interval*(i+3):interval*(i+3)+4])*(1-0.00013)
    
                        price_stop.append(price_stop_1)
                        
                        return_after_section.append((price_stop[-1]-price_stop[-2])*((3-n)/3)/price_stop[-2])
                        n = n+1
                if n == 3:
                    break
                if (data[day]['high'].iloc[interval*(i+3)-1] - minlow) > ATR*2:
                        price_stop_2 = np.average(data[day]['close'][interval*(i+3):interval*(i+3)+4], weights=data[day]['vol'][interval*(i+3):interval*(i+3)+4])*(1-0.00013)
                        price_stop.append(price_stop_2)
                            
                        return_after_section.append((price_stop[-1] - price_stop[-2])*((3-n)/3)/price_stop[-2])
                        n = n+1
                            
                if n == 3:
                    break
            price_stop_0 = np.average(data[day]['close'][-5::], weights=data[day]['vol'][-5::])*(1-0.00013)
            return_after_section.append((price_stop_0 - price_stop[-1])*((3-n)/3)/price_stop[-1])
            return_after_all_1 = sum(return_after_section)
            return_after_all.append(return_after_all_1)
            num_n.append(n)
            
            
            
        else:
            df_data.loc[day,'flag'] = 0
            return_after_all.append(0)
            num_n.append(0)
            
    df_data['date'] = return_date
    df_data['return_begin'] = return_begin
    df_data['return_after'] = return_after
    df_data['return_after_all'] = return_after_all
    df_data['num_n'] = num_n
    df_data['open'] = return_open
    df_data['close'] = return_close

        
    #将列表转化为矩阵，并赋予列名
    pd_buy = pd.DataFrame(record_buy, columns = ['date_buy','price_buy','price_close_buy'])
    pd_sell = pd.DataFrame(record_sell, columns = ['date_sell','price_sell','price_close_sell'])
    pd_transactions = pd.concat([pd_buy, pd_sell], axis = 1)  #pd.concat：连接函数，将买卖记录整合为交易记录


    #data['simple_return'] = data.close.pct_change(1).fillna(0)
    df_data['nav'] = (1+df_data.return_after_all.fillna(0)*df_data.flag).cumprod()
    df_data['benchmark'] = df_data.close / df_data.close[0] #将CLOSE[0]的净值设定为1，计算基准净值
    
    
    stats = evaluation(pd_buy,pd_sell, df_data) #计算评价指标
    # Output into Excel
    with pd.ExcelWriter("开盘动量_stop.xlsx") as writer:
        df_data.to_excel(writer, sheet_name='stock_data')
        pd_transactions.to_excel(writer, sheet_name='trade_record')
        stats.to_excel(writer, sheet_name='evaluations')

    return df_data,pd_transactions,stats



#加上止损和隔夜
def opendriven_stop_night(begin,interval,df_list,df_data):
    data = df_list.copy()
    df_data = df_data.iloc[0:-1]
    
    df_data['flag'] = 0 # 持仓标记，持多仓：1，不持仓：0，持空仓：-1
    record_buy = []
    record_sell = []
    
    return_begin = []
    return_after = []
    return_after_all = []
    return_date = []
    return_open = []
    return_close = []
    num_n = []
    for day in range(len(data)-1):
        begin_open_price = np.average(data[day]['open'][0:5],weights = data[day]['vol'][0:5])
        begin_close_price = np.average(data[day]['close'][begin-5:begin],weights = data[day]['vol'][begin-5:begin])
        return_begin_1 = (begin_close_price*(1-0.00013)-begin_open_price*1.00013)/begin_open_price*1.00013
        #加上双边交易费1.3%%
        after_open_price = np.average(data[day]['open'][begin:begin+4],weights = data[day]['vol'][begin:begin+4])
        after_close_price = np.average(data[day]['close'][-5::],weights = data[day]['vol'][-5::])
        return_after_1 = (after_close_price*(1-0.00013) - after_open_price*1.00013) / after_open_price*1.00013
        return_begin.append(return_begin_1)
        return_after.append(return_after_1)
       
        return_date.append(data[day]['date'].iloc[0])
        return_open.append(data[day]['open'].iloc[0])
        return_close.append(data[day]['close'].iloc[-1])
    
        
        
         #开多仓
        if min(data[day]['low'][0:interval]) < min(data[day]['low'][interval:interval*2]) < min(data[day]['low'][interval*2:interval*3]) \
            and data[day]['close'].iloc[interval-1] < data[day]['close'].iloc[interval*2-1] < data[day]['close'].iloc[interval*3-1] \
                and data[day]['open'].iloc[0] < data[day]['open'].iloc[interval] < data[day]['open'].iloc[interval*2]:

            df_data.loc[day,'flag'] = 1
            date_in = data[day]['date'].iloc[0]  #记录买入日期
            
           
            #记录买入价格
            price_in = np.average(data[day]['close'][interval*3:interval*3+4],weights = data[day]['vol'][interval*3:interval*3+4])*1.00013
           
            price_close_buy = np.average(data[day]['close'][-5::],weights = data[day]['vol'][-5::])*(1-0.00013)
             #记录平仓价格
            record_buy.append([date_in, price_in,price_close_buy])  #将日期和价格以列表形式添加到买入记录
           
            
            price_stop = [np.average(data[day]['close'][begin-5:begin], weights=data[day]['vol'][begin-5:begin])*(1-0.00013)]
            return_after_section = []
            
            n = 0
            TR = []
            for i in range(int(len(data[day]['high'])/interval-5)):
                #衰弱止损指标计算
                high_low = max(data[day]['high'][0:interval*(i+5)]) - min(data[day]['low'][0:interval*(i+5)])
                preclose_high = np.abs(data[day-1]['close'].iloc[-1] - max(data[day]['high'][0:interval*(i+5)]))
                preclose_low = np.abs(data[day-1]['close'].iloc[-1] - min(data[day]['low'][0:interval*(i+5)]))
                TR_1 = max(high_low,preclose_high,preclose_low)
                TR.append(TR_1)
                maxhigh = max(data[day]['high'][0:interval*(i+5)])
                ATR=np.sum(TR)/(i+1)


                #反向止损
                if max(data[day]['high'][interval*i:interval*(i+1)]) >= max(data[day]['high'][interval*(i+1):interval*(i+2)]) \
                >= max(data[day]['high'][interval*(i+2):interval*(i+3)]) >= max(data[day]['high'][interval*(i+3):interval*(i+4)]) \
                >= max(data[day]['high'][interval*(i+4):interval*(i+5)]):
                                
                            price_stop_1 = np.average(data[day]['close'][interval*(i+5):interval*(i+5)+4], weights=data[day]['vol'][interval*(i+5):interval*(i+5)+4])*(1-0.00013)
                            price_stop.append(price_stop_1)
                                
                            return_after_section.append((price_stop[-1] - price_stop[-2])*((3-n)/3)/price_stop[-2])
                            n = n+1
                if n == 3:
                    break
                if (maxhigh - data[day]['low'].iloc[interval*(i+5)-1]) > ATR*2.5:
                            price_stop_2 = np.average(data[day]['close'][interval*(i+5):interval*(i+5)+4], weights=data[day]['vol'][interval*(i+5):interval*(i+5)+4])*(1-0.00013)
                            price_stop.append(price_stop_2)
                                    
                            return_after_section.append((price_stop[-1] - price_stop[-2])*((3-n)/3)/price_stop[-2])
                            n = n+1
                                    
                if n == 3:
                    break
                                
            
            price_stop_0 = np.average(data[day+1]['open'][0:5], weights=data[day+1]['vol'][0:5])*(1-0.00013)
            return_after_section.append((price_stop_0 - price_stop[-1])*((3-n)/3)/price_stop[-1])
            
            return_after_all_1 = sum(return_after_section)
            return_after_all.append(return_after_all_1)
            num_n.append(n)
        #开空仓
        elif data[day]['close'].iloc[interval-1] > data[day]['close'].iloc[interval*2-1] > data[day]['close'].iloc[interval*3-1] \
            and max(data[day]['high'][0:interval]) > max(data[day]['high'][interval:interval*2]) > max(data[day]['high'][interval*2:interval*3]) \
                and data[day]['open'].iloc[0] > data[day]['open'].iloc[interval] > data[day]['open'].iloc[interval*2]:
            
        
            df_data.loc[day,'flag'] = -1
            date_out = data[day]['date'].iloc[0]  #记录卖出日期
            price_out = np.average(data[day]['close'][interval*3:interval*3+4],weights = data[day]['vol'][interval*3:interval*3+4])*(1-0.00013)
            #记录卖出价格
            price_close_sell = np.average(data[day]['close'][-5::],weights = data[day]['vol'][-5::])*(1+0.00013)  #记录平仓价格
            record_sell.append([date_out, price_out,price_close_sell])  #将日期和价格以列表形式添加到买入记录
            n = 0
            TR = []
            price_stop = [np.average(data[day]['close'][begin-5:begin], weights=data[day]['vol'][begin-5:begin])*(1-0.00013)]
            return_after_section = []
            for i in range(int(len(data[day]['high'])/interval-3)):
                high_low = max(data[day]['high'][0:interval*(i+3)]) - min(data[day]['low'][0:interval*(i+3)])
                preclose_high = np.abs(data[day-1]['close'].iloc[-1] - max(data[day]['high'][0:interval*(i+3)]))
                preclose_low = np.abs(data[day-1]['close'].iloc[-1] - min(data[day]['low'][0:interval*(i+3)]))
                TR_1 = max(high_low,preclose_high,preclose_low)
                TR.append(TR_1)
                minlow = min(data[day]['low'][0:interval*(i+3)])
                ATR=np.sum(TR)/(i+1)

                #反向止损
                if min(data[day]['low'][interval*i:interval*(i+1)]) <= min(data[day]['low'][interval*(i+1):interval*(i+2)]) \
                    and min(data[day]['low'][interval*(i+1):interval*(i+2)]) <= min(data[day]['low'][interval*(i+2):interval*(i+3)]):
                        price_stop_1 = np.average(data[day]['close'][interval*(i+3):interval*(i+3)+4], weights=data[day]['vol'][interval*(i+3):interval*(i+3)+4])*(1-0.00013)
    
                        price_stop.append(price_stop_1)
                        
                        return_after_section.append((price_stop[-1]-price_stop[-2])*((3-n)/3)/price_stop[-2])
                        n = n+1
                if n == 3:
                    break
                if (data[day]['high'].iloc[interval*(i+3)-1] - minlow) > ATR*2:
                        price_stop_2 = np.average(data[day]['close'][interval*(i+3):interval*(i+3)+4], weights=data[day]['vol'][interval*(i+3):interval*(i+3)+4])*(1-0.00013)
                        price_stop.append(price_stop_2)
                            
                        return_after_section.append((price_stop[-1] - price_stop[-2])*((3-n)/3)/price_stop[-2])
                        n = n+1
                            
                if n == 3:
                    break
            price_stop_0 = np.average(data[day]['close'][-5::], weights=data[day]['vol'][-5::])*(1-0.00013)
            return_after_section.append((price_stop_0 - price_stop[-1])*((3-n)/3)/price_stop[-1])
            return_after_all_1 = sum(return_after_section)
            return_after_all.append(return_after_all_1)
            num_n.append(n)
            
            
            
        else:
            df_data.loc[day,'flag'] = 0
            return_after_all.append(0)
            num_n.append(0)
            
    df_data['date'] = return_date
    df_data['return_begin'] = return_begin
    df_data['return_after'] = return_after
    df_data['return_after_all'] = return_after_all
    df_data['num_n'] = num_n
    df_data['open'] = return_open
    df_data['close'] = return_close

        
    #将列表转化为矩阵，并赋予列名
    pd_buy = pd.DataFrame(record_buy, columns = ['date_buy','price_buy','price_close_buy'])
    pd_sell = pd.DataFrame(record_sell, columns = ['date_sell','price_sell','price_close_sell'])
    pd_transactions = pd.concat([pd_buy, pd_sell], axis = 1)  #pd.concat：连接函数，将买卖记录整合为交易记录


    #data['simple_return'] = data.close.pct_change(1).fillna(0)
    df_data['nav'] = (1+df_data.return_after_all.fillna(0)*df_data.flag).cumprod()
    df_data['benchmark'] = df_data.close / df_data.close[0] #将CLOSE[0]的净值设定为1，计算基准净值
    
    
    stats = evaluation(pd_buy,pd_sell, df_data) #计算评价指标
    # Output into Excel
    with pd.ExcelWriter("开盘动量_stop_night.xlsx") as writer:
        df_data.to_excel(writer, sheet_name='stock_data')
        pd_transactions.to_excel(writer, sheet_name='trade_record')
        stats.to_excel(writer, sheet_name='evaluations')

    return df_data,pd_transactions,stats




#加上止损和隔夜和杠杆
def opendriven_stop_night_lever(begin,interval,df_list,df_data):
    data = df_list.copy()
    df_data = df_data.iloc[0:-1]
    
    df_data['flag'] = 0 # 持仓标记，持多仓：1，不持仓：0，持空仓：-1
    record_buy = []
    record_sell = []
    
    return_begin = []
    return_after = []
    return_after_all = []
    return_date = []
    return_open = []
    return_close = []
    num_n = []
    
    return_total = []
    lev_atr = [0]*(len(data)-1)
    tr_list = []
    atr_list = []
    
    for day in range(len(data)-1):
        
        total_open_price = data[day]['open'].iloc[0]
        total_close_price = data[day]['close'].iloc[-1]
        return_total_1 = (total_close_price - total_open_price)/total_open_price
        return_total.append(return_total_1)
        
            
        
        
        
        begin_open_price = np.average(data[day]['open'][0:5],weights = data[day]['vol'][0:5])
        begin_close_price = np.average(data[day]['close'][begin-5:begin],weights = data[day]['vol'][begin-5:begin])
        return_begin_1 = (begin_close_price*(1-0.00013)-begin_open_price*1.00013)/begin_open_price*1.00013
        #加上双边交易费1.3%%
        after_open_price = np.average(data[day]['open'][begin:begin+4],weights = data[day]['vol'][begin:begin+4])
        after_close_price = np.average(data[day]['close'][-5::],weights = data[day]['vol'][-5::])
        return_after_1 = (after_close_price*(1-0.00013) - after_open_price*1.00013) / after_open_price*1.00013
        return_begin.append(return_begin_1)
        return_after.append(return_after_1)
       
        return_date.append(data[day]['date'].iloc[0])
        return_open.append(data[day]['open'].iloc[0])
        return_close.append(data[day]['close'].iloc[-1])
        
        
        #衰弱止损指标计算
        high_low = max(data[day]['high']) - min(data[day]['low'])
        preclose_high = np.abs(data[day-1]['close'].iloc[-1] - max(data[day]['high']))
        preclose_low = np.abs(data[day-1]['close'].iloc[-1] - min(data[day]['low']))
        TR = max(high_low,preclose_high,preclose_low)
        tr_list.append(TR)
        
        if day <= 16:
            ATR = 200
        else:
            ATR = np.sum(tr_list[-17:-1])/16
        atr_list.append(ATR)
        
         #开多仓
        if min(data[day]['low'][0:interval]) < min(data[day]['low'][interval:interval*2]) < min(data[day]['low'][interval*2:interval*3]) \
            and data[day]['close'].iloc[interval-1] < data[day]['close'].iloc[interval*2-1] < data[day]['close'].iloc[interval*3-1] \
                and data[day]['open'].iloc[0] < data[day]['open'].iloc[interval] < data[day]['open'].iloc[interval*2]:
    
            df_data.loc[day,'flag'] = 1
            date_in = data[day]['date'].iloc[0]  #记录买入日期
            
           
            #记录买入价格
            price_in = np.average(data[day]['close'][interval*3:interval*3+4],weights = data[day]['vol'][interval*3:interval*3+4])*1.00013
           
            price_close_buy = np.average(data[day]['close'][-5::],weights = data[day]['vol'][-5::])*(1-0.00013)
             #记录平仓价格
            record_buy.append([date_in, price_in,price_close_buy])  #将日期和价格以列表形式添加到买入记录
           
            
            #记录lev_str
            lev_atr_1 = 0.005/ATR*price_in
            lev_atr[day] = lev_atr_1
            
            price_stop = [np.average(data[day]['close'][begin-5:begin], weights=data[day]['vol'][begin-5:begin])*(1-0.00013)]
            return_after_section = []
            
            n = 0
            
    
            
            
            for i in range(int(len(data[day]['high'])/interval-5)):
                
                maxhigh = max(data[day]['high'][0:interval*(i+5)])
    
               
            #反向止损
                if max(data[day]['high'][interval*i:interval*(i+1)]) >= max(data[day]['high'][interval*(i+1):interval*(i+2)]) \
                >= max(data[day]['high'][interval*(i+2):interval*(i+3)]) >= max(data[day]['high'][interval*(i+3):interval*(i+4)]) \
                >= max(data[day]['high'][interval*(i+4):interval*(i+5)]):
                                
                            price_stop_1 = np.average(data[day]['close'][interval*(i+5):interval*(i+5)+4], weights=data[day]['vol'][interval*(i+5):interval*(i+5)+4])*(1-0.00013)
                            price_stop.append(price_stop_1)
                                
                            return_after_section.append((price_stop[-1] - price_stop[-2])*((3-n)/3)/price_stop[-2])
                            n = n+1
                if n == 3:
                    break
                if (maxhigh - data[day]['low'].iloc[interval*(i+5)-1]) > ATR*2.5:
                            price_stop_2 = np.average(data[day]['close'][interval*(i+5):interval*(i+5)+4], weights=data[day]['vol'][interval*(i+5):interval*(i+5)+4])*(1-0.00013)
                            price_stop.append(price_stop_2)
                                    
                            return_after_section.append((price_stop[-1] - price_stop[-2])*((3-n)/3)/price_stop[-2])
                            n = n+1
                                    
                if n == 3:
                    break
                                
            
            price_stop_0 = np.average(data[day+1]['open'][0:5], weights=data[day+1]['vol'][0:5])*(1-0.00013)
            return_after_section.append((price_stop_0 - price_stop[-1])*((3-n)/3)/price_stop[-1])
            
            return_after_all_1 = sum(return_after_section)
            return_after_all.append(return_after_all_1)
            num_n.append(n)
        #开空仓
        elif data[day]['close'].iloc[interval-1] > data[day]['close'].iloc[interval*2-1] > data[day]['close'].iloc[interval*3-1] \
            and max(data[day]['high'][0:interval]) > max(data[day]['high'][interval:interval*2]) > max(data[day]['high'][interval*2:interval*3]) \
                and data[day]['open'].iloc[0] > data[day]['open'].iloc[interval] > data[day]['open'].iloc[interval*2]:
            
        
            df_data.loc[day,'flag'] = -1
            date_out = data[day]['date'].iloc[0]  #记录卖出日期
            price_out = np.average(data[day]['close'][interval*3:interval*3+4],weights = data[day]['vol'][interval*3:interval*3+4])*(1-0.00013)
            #记录卖出价格
            price_close_sell = np.average(data[day]['close'][-5::],weights = data[day]['vol'][-5::])*(1+0.00013)  #记录平仓价格
            record_sell.append([date_out, price_out,price_close_sell])  #将日期和价格以列表形式添加到买入记录
            
            #记录lev_str
            lev_atr_1 = 0.005/ATR*price_out
            lev_atr[day] = lev_atr_1
            
    
            n = 0
            price_stop = [np.average(data[day]['close'][begin-5:begin], weights=data[day]['vol'][begin-5:begin])*(1-0.00013)]
            return_after_section = []
            for i in range(int(len(data[day]['high'])/interval-3)):
    
                minlow = min(data[day]['low'][0:interval*(i+3)])
               
    
            #反向止损
                if min(data[day]['low'][interval*i:interval*(i+1)]) <= min(data[day]['low'][interval*(i+1):interval*(i+2)]) \
                    and min(data[day]['low'][interval*(i+1):interval*(i+2)]) <= min(data[day]['low'][interval*(i+2):interval*(i+3)]):
                        price_stop_1 = np.average(data[day]['close'][interval*(i+3):interval*(i+3)+4], weights=data[day]['vol'][interval*(i+3):interval*(i+3)+4])*(1-0.00013)
    
                        price_stop.append(price_stop_1)
                        
                        return_after_section.append((price_stop[-1]-price_stop[-2])*((3-n)/3)/price_stop[-2])
                        n = n+1
                if n == 3:
                    break
                if (data[day]['high'].iloc[interval*(i+3)-1] - minlow) > ATR*2:
                        price_stop_2 = np.average(data[day]['close'][interval*(i+3):interval*(i+3)+4], weights=data[day]['vol'][interval*(i+3):interval*(i+3)+4])*(1-0.00013)
                        price_stop.append(price_stop_2)
                            
                        return_after_section.append((price_stop[-1] - price_stop[-2])*((3-n)/3)/price_stop[-2])
                        n = n+1
                            
                if n == 3:
                    break
            price_stop_0 = np.average(data[day]['close'][-5::0], weights=data[day]['vol'][-5::0])*(1-0.00013)
            return_after_section.append((price_stop_0 - price_stop[-1])*((3-n)/3)/price_stop[-1])
            return_after_all_1 = sum(return_after_section)
            return_after_all.append(return_after_all_1)
            num_n.append(n)
            
            
            
        else:
            df_data.loc[day,'flag'] = 0
            return_after_all.append(0)
            num_n.append(0)
            
    df_data['date'] = return_date
    df_data['return_total'] = return_total
    df_data['return_begin'] = return_begin
    df_data['return_after'] = return_after
    
    
    vol = []
    mul = []
    vol = df_data['return_total'].rolling(window=252,center=False).std()*np.sqrt(252)
    for i in range(251):
        vol[i] = df_data['return_total'].iloc[0:253].std()*np.sqrt(252)
    mul = 0.15/vol
    
    mul = np.array(mul)
    lev_atr = np.array(lev_atr)
    return_after_all = np.array(return_after_all)
    lev = mul*lev_atr*10
    return_after_all = list(return_after_all*lev)
    
    df_data['mul'] = mul
    df_data['lev_atr'] = lev_atr
    df_data['lev'] = lev
    df_data['atr'] = atr_list
    df_data['return_after_all'] = return_after_all
    
    df_data['num_n'] = num_n
    #df_data['return_after_cost'] = return_after_cost
    df_data['open'] = return_open
    df_data['close'] = return_close
        
        
    #将列表转化为矩阵，并赋予列名
    pd_buy = pd.DataFrame(record_buy, columns = ['date_buy','price_buy','price_close_buy'])
    pd_sell = pd.DataFrame(record_sell, columns = ['date_sell','price_sell','price_close_sell'])
    pd_transactions = pd.concat([pd_buy, pd_sell], axis = 1)  #pd.concat：连接函数，将买卖记录整合为交易记录


    #data['simple_return'] = data.close.pct_change(1).fillna(0)
    df_data['nav'] = (1+df_data.return_after_all.fillna(0)*df_data.flag).cumprod()
    df_data['benchmark'] = df_data.close / df_data.close[0] #将CLOSE[0]的净值设定为1，计算基准净值
    
    
    stats = evaluation(pd_buy,pd_sell, df_data) #计算评价指标
    # Output into Excel
    with pd.ExcelWriter("开盘动量_stop_night_lever.xlsx") as writer:
        df_data.to_excel(writer, sheet_name='stock_data')
        pd_transactions.to_excel(writer, sheet_name='trade_record')
        stats.to_excel(writer, sheet_name='evaluations')

    return df_data,pd_transactions,stats










