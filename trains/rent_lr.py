import tensorflow as tf
from sklearn.utils import shuffle
from copy import deepcopy
import config
import pandas as pd
import numpy as np
from utils import ml

batch_size = 256

data = deepcopy(config.HOUSE_DF)
data['label'] = data['price'] / data['area']
data.drop('address', axis=1, inplace=True)
data.drop('url', axis=1, inplace=True)
data.drop('Unnamed: 0', axis=1, inplace=True)
data.drop('price', axis=1, inplace=True)
data.drop('location', axis=1, inplace=True)
data.drop('average_price', axis=1, inplace=True)

data_temp = pd.get_dummies(data.face)

for i in data_temp.columns:
    data[i] = data_temp[i]

data.drop('face', axis=1, inplace=True)

data = data.dropna()

data = shuffle(data)

data_train = data[:3400]
data_test = data[3400:]


def next(batch_size=batch_size, data=None):
    data_sample = data.sample(batch_size)
    return np.array(data_sample.drop('label', axis=1)), np.array(data_sample.label)


x = tf.placeholder(shape=[batch_size, 19], dtype=tf.float32)
y_ = tf.placeholder(shape=[batch_size], dtype=tf.float32)

w = tf.Variable(tf.random_uniform([19], -1.0, 1.0))
b = tf.Variable(tf.random_uniform([1], -1.0, 1.0))

X = tf.nn.tanh(ml.bn(x))
Y_ = ml.bn(y_)

o = tf.reduce_sum(X * w, axis=1) + b

y = o

loss = tf.reduce_mean((y - Y_) ** 2)

optimizer = tf.train.AdamOptimizer(learning_rate=0.001).minimize(loss)

sess = tf.Session()
sess.run(tf.global_variables_initializer())

for i in range(10 ** 10):
    a, b = next(data=data_train)
    sess.run(optimizer, feed_dict={x: a, y_: b})
    if i % 100 == 0:
        a_test, b_test = next(data=data_test)
        y_train, y_train_, loss_train = sess.run((y, Y_, loss), feed_dict={x: a, y_: b})
        y_test, y_test_, loss_test = sess.run((y, Y_, loss), feed_dict={x: a_test, y_: b_test})
        # q_train = np.mean(np.abs(z_train - z_train_))
        # q_test = np.mean(np.abs(z_test - z_test_))
        print(loss_train, loss_test, np.corrcoef(y_test, y_test_)[0, 1])
