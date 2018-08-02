import hashlib
import base64
import requests
import time
import pymongo

client = pymongo.MongoClient('mongodb://root:xingqiaodb2018@120.76.231.5/admin')
col = client.house.lianjia

def get_token(params):
    data = list(params.items())
    data.sort()

    app_id='20161001_android'
    token = '7df91ff794c67caee14c3dacd5549b35'

    for entry in data:
        token += '{}={}'.format(*entry)

    token = hashlib.sha1(token.encode()).hexdigest()
    token = '{}:{}'.format(app_id, token)
    token = base64.b64encode(token.encode()).decode()

    return token


def info(house_code):
    house_code = str(house_code)
    url = 'https://app.api.lianjia.com/house/zufang/detailpart1?house_code=' + house_code
    headers = {'Page-Schema': 'RentalHouseTransactionsActivity',
               'Cookie': 'lianjia_udid=868404029929838;lianjia_ssid=a67e1f35-3cdf-4d92-acd6-78c195900126;lianjia_uuid=dc91bdd0-b9e1-4192-87b0-f481f559dc80',
               'extension': 'lj_device_id_android=868404029929838&mac_id=48:DB:50:A4:B3:25&lj_imei=868404029929838&lj_android_id=3174db45c99fbc33',
               'User-Agent': 'HomeLink8.5.6;HUAWEI HUAWEI+NXT-AL10; Android 7.0',
               'Lianjia-Channel': 'Android_Huawei',
               'Lianjia-Device-Id': '868404029929838',
               'Lianjia-Version': '8.5.6',
               'Authorization': get_token({'house_code':house_code}),
               'Lianjia-Im-Version': '2.14.2',
               'Host': 'app.api.lianjia.com',
               'Connection': 'Keep-Alive',
               'Accept-Encoding': 'gzip'}
    data=requests.get(url,headers=headers).json()['data']

    col_to_del={'picture_list','deal_info','user_related'}

    for i in col_to_del & set(data):
        data.pop(i)
    return data

while True:
    t0 = time.time()
    dic = {i['_id']: i for i in col.find({'times': 0, 'lock': 0}).limit(20)}
    t1 = time.time()
    col.update_many({'_id': {'$in': list(dic.keys())}}, {'$set': {'lock': 1}})
    t2 = time.time()

    data={}
    for i in dic:
        try:
            data[i]=info(i)
            data[i]['times']=dic[i]['times']+1
            data[i]['lock']=0
        except KeyboardInterrupt:
            quit()
        except Exception as e:
            print(e)

    t3=time.time()
    for i in data:
        col.update_one({'_id': i}, {'$set': data[i]})

    t4=time.time()
    print(t1-t0,t2-t1,t3-t2,t4-t3,t4-t0,len(data)/(t4-t0))

