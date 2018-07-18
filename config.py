import pandas as pd
import os
from utils import fts

ROOT_PATH=os.path.dirname(__file__)
#GAODE_KEY='7dcbbfaf8d5140e031f0d8f2ea972780'
GAODE_KEY='28b07e24f4fb819ea8516b9715d77ca3'

HOUSE_SALE=pd.read_csv(ROOT_PATH+'/data_sets/anjuke_sale_preprocessing.csv')
HOUSE_RENT=pd.read_csv(ROOT_PATH+'/data_sets/anjuke_rent_preprocessing.csv')

MODEL_SALE_XGB=ROOT_PATH+'/model/xgb_sale'

if fts.get_host_ip()=='120.76.231.5':
    PORT='80'
else:
    PORT='8090'