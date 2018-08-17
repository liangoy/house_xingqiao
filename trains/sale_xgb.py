import xgboost as xgb
import pandas as pd
import numpy as np
from copy import deepcopy
import config
from sklearn.utils import shuffle
from utils import fts
import time

data = pd.read_csv(config.ROOT_PATH + '/data_sets/fangdd_sale.csv')
data = data[sorted(data.columns)]
data.dropna(subset=['trade_date'], inplace=True)

data=data[(10000<data.average_price) & (data.average_price<150000)]

data['trade_date'] = [time.mktime(tuple([int(i) for i in (t + '-01-01').split('-')[:3]]) + (0, 0, 0, 0, 0, 0)) for t in
                      data.trade_date]

data.index = range(len(data.index))

cnt = 0
for i in ['face', 'floor_type']:
    df_temp = pd.DataFrame(fts.one_hot(data[i]))
    for j in df_temp.columns:
        data[str(cnt)] = df_temp[j]
        cnt += 1

for i in ['_id', 'address', 'Unnamed: 0', 'community', 'floor', 'region', 'times', 'title', 'type', 'lock',
          'total_price', 'face', 'floor_type']:
    data.drop(i, axis=1, inplace=True)

data = shuffle(data)

data_train = data[:len(data)//10*7]
data_test = data[len(data)//10*7:]

y_train_ = np.array(data_train['average_price'])
x_train = np.array(data_train.drop('average_price',axis=1))

y_test_ = np.array(data_test['average_price'])
x_test = np.array(data_test.drop('average_price',axis=1))

params = {
    'booster': 'gbtree',
    'objective': 'reg:linear',
    #'eval_metric':'rmse',
    'eval_metric':'mae',#衡量准确度的方法
    'gamma': 0.1,
    'max_depth': 6,
    'alpha': 1,# l1正则
    'lambda': 10,#l2正则
    'subsample': 1,
    #'colsample_bytree': 0.7,
    'min_child_weight': 3,
    'silent': 1,#是否静默
    'eta': 0.1,#range(0,1) default 0.3  weight of tree
    'seed': 1000,
    'nthread': 8,
    #'scoring':'neg_mean_squared_error'
}

dtrain = xgb.DMatrix(x_train, y_train_)
dtest = xgb.DMatrix(x_test,y_test_)
num_rounds = 10000

plst = params.items()
model = xgb.train(plst, dtrain, num_rounds,evals=[(dtrain, 'train'),(dtest,'test')])

# 对测试集进行预测
ans = model.predict(dtest)

y_test=np.array(ans)

print(np.mean(np.abs(y_test-y_test_)))
print(np.corrcoef(y_test,y_test_)[0,1])