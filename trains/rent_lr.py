import tensorflow as tf
from sklearn.utils import shuffle
from copy import deepcopy
import config
import pandas as pd
import numpy as np
from utils import ml

batch_size = 4096

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
lis.append(pd.get_dummies(data.face))
lis.append(pd.get_dummies(data.decoration))
lis.append(pd.get_dummies(data.floor_type))

data_temp=pd.concat(lis,axis=1)

data_temp = pd.get_dummies(data.face)
for i in data_temp.columns:
    data[i] = data_temp[i]

data.drop('face', axis=1, inplace=True)
data.drop('decoration', axis=1, inplace=True)
data.drop('floor_type', axis=1, inplace=True)

data = data.dropna()

data = shuffle(data)

data_train = data[:len(data)//10*7]
data_test = data[len(data)//10*7:]

shape_x=data_train.shape[1]-1

def next(batch_size=batch_size, data=None):
    data_sample = data.sample(batch_size)
    return np.array(data_sample.drop('label', axis=1)), np.array(data_sample.label)


x = tf.placeholder(shape=[batch_size, shape_x], dtype=tf.float32)
y_ = tf.placeholder(shape=[batch_size], dtype=tf.float32)

X = tf.nn.tanh(ml.bn(x))
Y_ = ml.bn(y_)

lay1=tf.nn.tanh( ml.layer_basic(X,32))
lay2=tf.nn.tanh(ml.layer_basic(lay1,16))
lay3=tf.nn.tanh(ml.layer_basic(lay2,4))
y = ml.layer_basic(lay3,1)[:,0]

loss = tf.reduce_mean((y-Y_)**2)


optimizer = tf.train.AdamOptimizer(learning_rate=0.01).minimize(loss)

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
