import xgboost as xgb
import pandas as pd
import numpy as np
from copy import deepcopy
import config
from sklearn.utils import shuffle
from utils import fts



data = deepcopy(config.HOUSE_SALE).dropna()

#data-preprocessing-----------------------------------------------------
data=data[data.area<300]
data=data[data.price<180000]
data=data[1981<=data.year]
data=data[data.rooms<=6]
data=data[data.living_rooms<=4]
data=data[data.wc<=7]
#####################################################################
print(len(data))


data['label'] = data['price']
data.drop('address', axis=1, inplace=True)
data.drop('Unnamed: 0', axis=1, inplace=True)
data.drop('price', axis=1, inplace=True)
data.drop('location', axis=1, inplace=True)


# data.drop('average_selling_price', axis=1, inplace=True)
# data.drop('average_rental_price', axis=1, inplace=True)


lis=[]
lis.append(pd.DataFrame(fts.one_hot(data.face)))
lis.append(pd.DataFrame(fts.one_hot(data.decoration)))
lis.append(pd.DataFrame(fts.one_hot(data.floor_type)))

data_temp=pd.concat(lis,axis=1)
data_temp.columns=range(len(data_temp.columns))

for i in data_temp.columns:
    data[i] = data_temp[i]

data.drop('face', axis=1, inplace=True)
data.drop('decoration', axis=1, inplace=True)
data.drop('floor_type', axis=1, inplace=True)

data = data.dropna()
data = shuffle(data)


data_train = data[:len(data)//10*7]
data_test = data[len(data)//10*7:]



y_train_ = np.array(data_train['label'])
x_train = np.array(data_train.drop('label',axis=1))


y_test_ = np.array(data_test['label'])
x_test = np.array(data_test.drop('label',axis=1))


params = {
    'booster': 'gbtree',
    'objective': 'reg:linear',
    #'eval_metric':'rmse',
    'eval_metric':'mae',
    'gamma': 0.1,
    'max_depth': 6,
    'lambda': 10,
    'subsample': 0.5,
    'colsample_bytree': 0.7,
    'min_child_weight': 3,
    'silent': 1,#是否静默
    'eta': 0.05,
    'seed': 1000,
    'nthread': 4,
    'scoring':'neg_mean_squared_error'
}

dtrain = xgb.DMatrix(x_train, y_train_)
dtest = xgb.DMatrix(x_test,y_test_)
num_rounds = 5000

plst = params.items()
model = xgb.train(plst, dtrain, num_rounds,evals=[(dtrain, 'train'),(dtest,'test')])

# 对测试集进行预测
ans = model.predict(dtest)

y_test=np.array(ans)

print(np.mean(np.abs(y_test-y_test_)))
print(np.corrcoef(y_test,y_test_)[0,1])

