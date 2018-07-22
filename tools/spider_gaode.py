import pymongo
import time
import requests

client = pymongo.MongoClient('mongodb://root:xingqiaodb2018@120.76.231.5/admin')
col = client.house.fangduoduo_shenzhen

while True:
    t0=time.time()
    ins=col.find_one_and_update({'lock':'0','times':'1'},{'$set':{'lock':'1'}})
    loc=str(ins['longitude'])+','+str(ins['latitude'])
    _id=ins['_id']
    t1=time.time()
    try:
        r=requests.get('http://120.76.231.5/house/around_info?location='+loc+'&radius=1000')
        r.close()
        data=r.json()
        print(data)
        d = {
            'bus_stop': data['公交站'],
            'hospital': data['医院'],
            'subway_station': data['地铁站'],
            'school': data['学校'],
            'hotel': data['宾馆'],
            'bank': data['银行'],
            'times': '2',
            'lock': '0',
        }
        col.update_one({'_id': _id}, {'$set': d})
    except KeyboardInterrupt:
        break
    except Exception as e:
        print('error:',e)
    t2=time.time()
    print(t1-t0,t2-t1,t2-t0,len(data))