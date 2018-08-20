from scipy.optimize import leastsq
import numpy as np
import pandas as pd
import config
from sklearn.utils import shuffle
from utils import fts, ml
import time

data = pd.read_csv(config.ROOT_PATH + '/data_sets/fangdd_sale.csv')
data.dropna(subset=['trade_date', 'around_price'], inplace=True)

data = data[(10000 < data.average_price) & (data.average_price < 150000)]
data.build_date.fillna(data.build_date.mean(), inplace=True)
data.living_rooms.fillna(0, inplace=True)
data = data[data.living_rooms <= 3]
data.rooms.fillna(0, inplace=True)
data.total_floor.fillna(data.total_floor.mean(), inplace=True)

data['trade_date'] = [time.mktime(tuple([int(i) for i in (t + '-01').split('-')[:3]]) + (0, 0, 0, 0, 0, 0)) for t in
                      data.trade_date]

data.index = range(len(data.index))

cnt = 0
for i in ['face', 'floor_type']:
    df_temp = pd.DataFrame(fts.one_hot(data[i]))
    for j in df_temp.columns:
        data[str(cnt)] = df_temp[j]
        cnt += 1

for i in ['address', 'Unnamed: 0', 'community', 'floor', 'region', 'times', 'title', 'type', 'lock',
          'total_price', 'face', 'floor_type', 'wcs','around_price']:
    data.drop(i, axis=1, inplace=True)

label_std = data.average_price.std()
label_mean = data.average_price.mean()

for i in data.columns:
    mean, std = data[i].mean(), data[i].std() + 0.0000000001
    data[i] = (data[i] - mean) / std

data = shuffle(data)

data_train = data[:len(data) // 10 * 7]
data_test = data[len(data) // 10 * 7:]

x_train = np.array(data_train.drop('average_price', axis=1))
y_train_ = np.array(data_train.average_price)

x_test = np.array(data_test.drop('average_price', axis=1))
y_test_ = np.array(data_test.average_price)

fn = lambda p, x: np.dot(x, p[:-1])+p[-1]
error_fn = lambda p, x, y: fn(p, x) - y
par, success = leastsq(error_fn, [0.0 for i in range(x_train.shape[1]+1)], args=(x_train, y_train_))
y_test = fn(par, x_test)
print(np.mean(np.abs(y_test - y_test_)) * label_std, np.corrcoef(y_test, y_test_)[0, 1])
