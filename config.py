import pandas as pd
import os
from utils import fts

ROOT_PATH=os.path.dirname(__file__)
#GAODE_KEY='7dcbbfaf8d5140e031f0d8f2ea972780'
GAODE_KEY='28b07e24f4fb819ea8516b9715d77ca3'

HOUSE_SALE=pd.read_csv(ROOT_PATH+'/data_sets/fangdd_sale.csv')

MODEL_SALE_XGB=ROOT_PATH+'/models/sale_xgb'

MONGO_STRING='mongodb://root:xingqiaodb2018@120.76.231.5/admin'

if fts.get_host_ip()=='120.76.231.5':
    PORT='80'
else:
    PORT='8090'

#1652.6692162245795
#0.8854629408607843

if __name__=='__main__':
    print('hello')