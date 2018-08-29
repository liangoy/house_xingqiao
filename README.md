# 摘要
这个项目是对房屋价格和租价的预测,包含了从爬虫到预测模型,再到api接口的全部代码.
从一些房多多以及链家取得了深圳市的房屋成交记录(40万)以及租赁成交记录(8.4万).
经过了简单处理后用了线性模型,神经网络,xgboost等等建立预测模型,并完成了模型预测价格的api接口.
本项目有代码粗陋,缺少注释以及git commit乱写等种种缺陷,这个文章权记录一下做这个项目的思路,如果对他人有帮助就再好不过了.
如果有任何关于提高模型的思路,如果能提出来,万分感激.

# 项目文件介绍
* data_sets:存放数据的文件夹,本来数据是放在mongodb上的,为了加快模型读取加快读取速度所以将数据用保存成csv格式.由于数据比较大,所以就没把数据放在工程里,数据可以从这里拿#todo
* handlers 存放处理api请求的文件
* models 存放训练完成的模型,由于数据比较大,所以就没把数据放在工程里,数据可以从这里拿#todo
* services 提供服务以供调用
* tools 存放一些脚本,在这项目中主要存放一些爬虫脚本
* trains 存放建立预测模型的代码
* utils 存放一些需要重复调用的函数
* config 配置文件
* api.yaml 基于swagger的api配置文件
* run.py 启动接口服务

# 爬取数据
爬取数据的脚本都放在tools里面
数据来源主要有三个
* 房多多的数据,这是房屋成交价格的数据
* 链家的数据,这部分是房屋租价的数据(在链家上成交)
* 高的的数据,高徳的数据主要做一些数据维度的补充,例如这套房子附近有多少公交站等等等
下面讲解这三个数据的具体爬取过程
##  房多多的数据
房多多房屋成交数据是这个样子的[房多多例子](http://shenzhen.fangdd.com/chengjiao/907510.html)
如果你把url中的'shenzhen'改成'beijing',他的页面仍然不变.
所以房多多房屋页面只取决与后面那窜数字.
所以我们只要从这个数字有页面的最小值遍历到最大值就可以把房多多所有的成交记录都拿出来.
求最小值和最大值用二分法去尝试吧,很快就能找出来.
大概有90w+的页面需要爬取.
这个时候显然用单机同步去爬取效率底下.
而爬取这些数据去搞什么分布式爬虫又没什么必要.
所以我采用了一个土方法,用数据库存储数据,再用一些锁保证不会同步爬取.然后就是你的爬虫进程向数据库请求一些没有被爬过的房屋的id,然后锁住这些记录防止其他爬虫进程再取得这些房屋id重复爬取.等到爬取完成再把数据存如数据库且开锁.这样你要在几台机器上爬就再几台机器上爬,要开几个进程就开几个进程(前提是数据库性能还没遇到瓶颈).
下面是具体实现:
1. 将房屋的id当成索引,并加入lock的段(表示锁的状态,0代表没锁,1代表锁)和times字段(表示爬取的次数)生成记录(大概90w+条),塞进数据库.
tip:在mongo中就用'_id'当成房屋的id的字段名称吧(mongo中的_id就是索引,省得自己去声明索引),
2. 爬虫进程从数据库中找出times为0,lock为0的记录
3. 根据房屋id爬取数据,然后塞进数据库,并把这些字段的times增加1,lock改为0.

这样子写好爬虫脚本,多放在几台机器上,多开几个进程跑,两三天就可以爬完了

## 链家的数据
链家上有租房成交记录.网页上没有,但是手机app上有,而链家的app是用https传输的.
所以这就比较麻烦一点点,要先用电脑下个抓包软件,然后安装假证书(这个过程百度一下就有).然后得到请求头和请求的url.url类似这个样子:https://app.api.lianjia.com/house/zufang/detailpart1?house_code='房屋id'
用requests改一下请求头然后访问一下url,果然成功!!
但是将url的参数随便该一下,会发现竟然报错了.
原来是链家的app用url的请求参数生成一个哈系摘要,然后将这个在要放在请求头中.
这就麻烦了,可能要反编译什么鬼的.
但不慌,有大神已经搞出来了#todo,我们拿来主义就好.
接下来还是根据房屋id遍历一边,总共得到8w+条记录.
## 高德数据
房屋附近的信息比如一公里内有多少银行,多少公交站等等很可能会对房屋的预测起到很好的帮助作用.
那这些数据要哪里拿呢?
高徳!
高徳是一家良心公司,提供了接口,写好了api文档等我们.
但就是要注册,个人帐号调用次数比较少,最好用公司的帐号注册.
然后就是根据房屋的地址生成经纬度信息,然后根据经纬度就可以得到各种各样的信息(我用到的只有例如方圆1公里有多少银行,学校,公交站,地铁站等等)
然后就调用接口就好了

# 数据预处理

## 房多多的数据预处理
原来爬得的数据有38.9w,去除重复重复的数据后还剩下25w(房多多储存了这么多的重复数据...).如下所示.
![fangdd_info](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_info.png)
* 'Unnamed: 0'是从csv中读到的索引,是无意义的,故而删除之.
* 'address'是房屋的地址,我们结合高徳将他转化成了经纬度.这个属性应该是可以进一步挖掘出信息的,例如可以将房屋分成南山区,罗湖区等等.
* 'area'是房屋的面积,没有缺失数据,其直方图如图所示![fangdd_area](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_area.png),我们并没有对其作出处理.
* 'around_price'是周围的房屋均价,这个是生成的数据.通过经纬度得到以所求房屋为中心,边长为500米内的房屋的均价(若房屋数量小于20,则均价为空值).其直方图如图所示![fangdd_around_price](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fanddd_around_price.png),均价为空值的数据比较少,所以我们直接将其删除.
* 'average_price'是房屋每平方米的价格.其直方图如图所示![fangdd_average_price_error](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_average_price_error.png),可见每平方米价格中有一个极大的异常值,我们去掉异常值(取值在[0,200000]中的数据)后再画出直方图![fangdd_average_price](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_average_price.png)可见在150000后的值已经很稀少了,所以我们将值大于150000的记录舍弃.
* 'bank'是周围银行的数量![fangdd_bank](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_bank.png)无需处理.
* 'build_date':如图所示![fangdd_build_date](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_build_date.png),build_date有八千多个缺失值,我们采用平均值填补这种比较粗糙的处理方法.如果时间充足,先对数据进行聚类,然后用类平均值去填充缺失值应该是一个更好的选择.
* 'bus_stop'是周围的公交站台的数量,如图所示![fangdd_bus_stop](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_bus_stop.png) 不做处理.
* 'community'是房屋所在社区,暂时弃之不用.
* 'face'是房屋朝向 '未知:0,北:1,东北:2,东:3,东南:4,南:5,西南:6,西:7,西北:8,东西:9,南北:10'  ![fangdd_face](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_face.png)
* 'floor'是楼层以及总楼层.已经根据floor生成floor_type和total_floor.故而弃之.
* 'floor_type'是楼层类型 '未知:0,地下室:1,低层:2,中层:3,高层:4,顶层:5' 其分布如图所示![fangdd_floor_type](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_floor_type.png).
* 'hospital'是房屋周围的医院数量,如图所示![fangdd_hospital](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_hospital.png).
* 'hotel'是房屋周围的宾馆数量,如图所示![fangdd_hotel](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_hotel.png)
* 'latitude'是房屋的维度,如图所示![fangdd_latitude](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_latitude.png)
* 'living_rooms'是房屋的客厅数量,如图所示![fangdd_living_rooms](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_living_rooms.png),其从有五万多缺失值,但没有living_rooms的值为0的记录,所以我们认为应该用0填充缺失值.living_rooms的值大于3的记录的数量只有一百多个,所以我们将living_rooms的值大于3的记录删除.
* 'lock'是爬虫中的锁,弃之.
* 'longitude'是经度,如图所示![fangdd_longitude](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_longitude.png)
* 'region'是房屋所在区域,弃之
* 'rooms'的分布如图所示![fangdd_rooms](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_rooms.png),rooms有缺失值,但没有零值,所以我们认为其缺失值即为0.
* 'school'是房屋周围得学校数量,如图所示![fangdd_school](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_school.png)
* 'subway_station'是房屋周围得地铁站得数量,如图所示![fangdd_subway_station](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_subway_station.png)
* 'times'是爬虫爬取得次数,弃之
* 'title'是爬取的房多多的u页面的标题,这个属性已经转化成floor,area等属性了,弃之.
* 'total_floor'是房屋所在的楼层的总层数,存在几万的缺失值,出于时间原因,我们采用总体均值去填充.如果时间充足,对数据进行聚类然后用类均值替代会好一点.
* 'total_price'可以由area和average_price相乘得到,故而弃之.
* 'trade_date'是交易时间,有四个缺失值,直接将缺失值删除,然后将其转化成时间戳.其分布如图所示![fangdd_trade_date](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_trade_date.png)
* 'type'是房屋的类型,其分布如图所示![fangdd_type](https://github.com/liangoy/house_xingqiao/blob/master/pictures/fangdd_type.png),这个属性太过凌乱,暂时不用.
* 'wcs'是房屋内的厕所数量,缺失值过多,弃之.

# 跑模型
所有模型的训练集和测试集的比例为7:3
本节主要对比各种模型在同一个数据集上的差别
## 线性回归
线性回归主要的作用是作为预测准确性的参照物
房价预测模型上的表现:平均误差为9323.504946203882,相关系数为0.7508103178808123
## xgboost
实现的文件在trains/sale_xgb.py.
train-mae:1170.42	test-mae:1939.84    相关系数:0.9856159960273403
在处理这种没有局部联系的信息上(反例就是图片),xgboost这种提升树类型的算法确实比神经网络厉害得多.
个人感觉是xgboost的这种贪婪地减少loss的算法已经可以接近完美地利用输入值的属性(穷尽了输入值不用属性的各种组合).
但对于有局部联系的数据(例如图片),其维度一般很高(例如长10宽10的三通道图片,其维度有10*10*3),xgboost可能会对没有关联的的属性(例如左上角的点与右下角的点)强行寻求其与loss的关系,将偶然当成规律,很容易造成过拟合.
而卷积神经网络已经被人为限定只能猜测卷积窗口中的那些属性与loss的关系,没有办法猜测没有关系的属性(例如左上角的点与右下角的点)与loss见的关系,不容易造成过拟合.
xgboost本质在于尝试各种切分数据的方法,然后找出能让loss下降最多的方法.神经网络在于由低层次的特征组合成高层次的特征.
所以我提出一个假说:相对于神经网络,xgboost不能学习到深层次的规律,也就是说在模型的假设环境不变的情况下,对于没有局部联系的信息上xgboost的性能会好于神经网络,但是一旦假设发生变化,xgboost模型的性能就会大幅度下降(有时间再证明).
如果假说成立,xgboost刷比赛可以,用于预测模型就要三思了.
## 神经网络
### 浅层神经网络
用浅层神经网络要解决几个问题:
* 如何设置网络层数?是要正三角行还是倒三角型还是梭子型还是沙漏形.




### 深层神经网络
在本节全部用残差神经网络去实现深层神经网络.
relu和bn处理基本解决了神经网络梯度爆炸和梯度消失的问题.但在一定的层数后,网络层数的加深并不能带来效果的提升,反而会降低网络的效果,这个现象制约了深层神经网络的发展.
为什么网络的层数变深效果反而变差?这个暂时好像没有很好的理论解释(有人用"[退化](https://www.jiqizhixin.com/articles/2018-01-07-2)"解释)
2015年何凯明博士的提出的残差神经网络为深层神经网络的实现提供了途径,是一个里程碑事件.
残差神经网络的特别机制就在于"短路".为什么短路机制能起效果,让网络的效果不随着层数的加深反而降低?何凯明博士认为网络对于误差的拟合比对自身值的拟合容易.例如真实值是5,预测5.1和预测5.2看起来效果差不多,
但如果按残差的角度看,前者是0.1,后者是0.2.差了一倍!很显著!所以对于残差的拟合比较容易.而残差神经网络中被短路的网络就是预测残差.这样看来其实短路机制就是误差的放大器.
其实这个原理在bn中也似曾相识,bn不也是将平均值置为0,让网络专心于误差而不用学习平均值.














# api接口
# 总结
