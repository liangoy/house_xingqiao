import tensorflow as tf

import pandas as pd
import numpy as np
from copy import deepcopy
import config
from sklearn.utils import shuffle
from utils import fts
import tensorflow as tf
from utils import ml

batch_size = 512

data = deepcopy(config.HOUSE_SALE).dropna()

# data-preprocessing-----------------------------------------------------
data = data[data.area < 300]
data = data[data.price < 180000]
data = data[1981 <= data.year]
data = data[data.rooms <= 6]
data = data[data.living_rooms <= 4]
data = data[data.wc <= 7]
#####################################################################
print(len(data))

data.drop('address', axis=1, inplace=True)
data.drop('Unnamed: 0', axis=1, inplace=True)
data.drop('location', axis=1, inplace=True)

# data.drop('average_selling_price', axis=1, inplace=True)
# data.drop('average_rental_price', axis=1, inplace=True)


lis = []
lis.append(pd.DataFrame(fts.one_hot(data.face)))
lis.append(pd.DataFrame(fts.one_hot(data.decoration)))
lis.append(pd.DataFrame(fts.one_hot(data.floor_type)))

data_temp = pd.concat(lis, axis=1)
data_temp.columns = range(len(data_temp.columns))

for i in data_temp.columns:
    data[i] = data_temp[i]

data.drop('face', axis=1, inplace=True)
data.drop('decoration', axis=1, inplace=True)
data.drop('floor_type', axis=1, inplace=True)

data = data.dropna()

label_mean = data.price.mean()
label_std = data.price.std()

for i in data.columns:
    data[i] = (data[i] - data[i].mean()) / data[i].std()

data['label'] = data['price']
data.drop('price', axis=1, inplace=True)

data = shuffle(data)

data_train = data[:len(data) // 10 * 7]
data_test = data[len(data) // 10 * 7:]

shape_x = data_train.shape[1] - 1


def next(batch_size=batch_size, data=None):
    data_sample = data.sample(batch_size)
    return np.array(data_sample.drop('label', axis=1)), np.array(data_sample.label)


x = tf.placeholder(shape=[batch_size, shape_x], dtype=tf.float32)
y_ = tf.placeholder(shape=[batch_size], dtype=tf.float32)

X=tf.reshape(x,[batch_size,1,shape_x,1])

c1=ml.conv2d(X,conv_filter=[1,shape_x,1,32],padding='VALID',ksize=[1,1,1,1],pool_padding='VALID')

lay1=tf.reshape(c1,[batch_size,32])

lay2 = tf.nn.elu(ml.layer_basic(lay1, 8))

lis = [lay2]
for i in range(20):
    lis.append(ml.res(lis[-1]))

y = ml.layer_basic(lis[-1], 1)[:, 0]

loss = tf.reduce_mean((y - y_) ** 2)

optimizer = tf.train.AdamOptimizer(learning_rate=0.01).minimize(loss)

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