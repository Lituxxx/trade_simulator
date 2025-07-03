'''
由于股票历史数据仅供训练所用，所有没有必要频繁更新数据。每个月只需要花十几分钟刷新一下数据
'''
import tushare as ts
import pandas as pd
import time
from datetime import date

pro = ts.pro_api('f95df333fd3fe823d921ae41e676147c44b397743b3f74de81e3e7f8')
start_date='20180101'#起始日期可自定义,没必要用太早的数据
stock_list = pd.read_excel("stocklist.xlsx")

for stockcode in stock_list['ts_code']:
    temp_data = pro.daily(ts_code=stockcode, start_date=start_date, end_date=date.today().strftime('%Y%m%d'))
    temp_data.to_csv(f'stockdata/{stockcode[:6]}.csv',index=False)#A股代码均为六位
    time.sleep(0.1)
    print(f'{stockcode} complete')