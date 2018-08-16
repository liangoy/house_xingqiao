import tensorflow as tf
import pandas as pd
import numpy as np
from copy import deepcopy
import config
from sklearn.utils import shuffle
from utils import fts, ml
import time

batch_size = 2048

data = pd.read_csv(config.ROOT_PATH + '/data_sets/fangdd_sale.csv')
data.dropna(subset=['trade_date'], inplace=True)

data = data[(10000 < data.average_price) & (data.average_price < 150000)]

data['trade_date'] = [time.mktime(tuple([int(i) for i in (t + '-01').split('-')[:3]]) + (0, 0, 0, 0, 0, 0)) for t in
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

for i in ['total_floor', 'area', 'build_date', 'rooms', 'living_rooms', 'around_price']:
    data[i] = data[i].fillna(data[i].mean())

label_std = data.average_price.std()
label_mean = data.average_price.mean()

for i in data.columns:
    mean, std = data[i].mean(), data[i].std() + 0.0000000001
    data[i] = (data[i] - mean) / std

data = shuffle(data)

data_train = data[:len(data) // 10 * 7]
data_test = data[len(data) // 10 * 7:]

shape_x = data_train.shape[1] - 1


def next(batch_size=batch_size, data=None):
    data_sample = data.sample(batch_size)
    return np.array(data_sample.drop('average_price', axis=1)), np.array(data_sample.average_price)


x = tf.placeholder(shape=[batch_size, shape_x], dtype=tf.float32)
y_ = tf.placeholder(shape=[batch_size], dtype=tf.float32)

lay1 = ml.layer_basic(ml.bn(x), 16)

lis = [lay1]
for i in range(30):
    lis.append(ml.res(lis[-1]))

y = ml.layer_basic(ml.bn(lis[-1]), 1)[:, 0]

loss = tf.reduce_mean((y - y_) ** 2)

optimizer = tf.train.AdamOptimizer(learning_rate=0.2).minimize(loss)

sess = tf.Session()
sess.run(tf.global_variables_initializer())

for i in range(10 ** 10):
    a, b = next(data=data_train)
    sess.run(optimizer, feed_dict={x: a, y_: b})
    if i % 100 == 0:
        a_test, b_test = next(data=data_test)
        y_train, y_train_, loss_train = sess.run((y, y_, loss), feed_dict={x: a, y_: b})
        y_test, y_test_, loss_test = sess.run((y, y_, loss), feed_dict={x: a_test, y_: b_test})

        print(np.mean(np.abs(y_train - y_train_)) * label_std, np.mean(np.abs(y_test - y_test_)) * label_std,
              np.corrcoef(y_test, y_test_)[0, 1])
