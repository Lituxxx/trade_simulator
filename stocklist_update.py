import tushare as ts
pro = ts.pro_api('f95df333fd3fe823d921ae41e676147c44b397743b3f74de81e3e7f8')
data = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code,name,area,industry,list_date')
data.to_excel("stocklist.xlsx",index=False)