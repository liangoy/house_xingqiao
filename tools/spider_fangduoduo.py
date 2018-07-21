import pymongo
import re
import time
import aiohttp
import asyncio
from lxml.etree import HTML as leh

db = pymongo.MongoClient('mongodb://root:xingqiaodb2018@120.76.231.5/admin')
col = db.house.fangduoduo

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
           'Cache-Control': 'max-age=0',
           'Connection': 'keep-alive',
           'Cookie': 'TP_AGENT_ID=5b505ad8ec250fe9bc0898ca; cityName="%E6%B7%B1%E5%9C%B3"; cityPinYin=shenzhen; cityPy=sz; city_id=1337; _fa=FA1.0.1531992802874.5731043432; _ga=GA1.2.1085765069.1531992804; _gid=GA1.2.1337044227.1531992804; TSUID=3d557156def24ecc; TSSES=17d57156def48fe8; mainwebwebsiteesffddToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ3ZWJjb2RldXVpZCI6IjVjZmE0MjE1LTkzMzMtNDVkZS04MTE4LWJiODM0Y2I2YzJlMSIsImlhdCI6MTUzMjA1MTEzNSwiZXhwIjoxNTMyNjU1OTM1fQ.s7Utsfk7nkuo_fhDXVsgDvyb14zpFGYIqzFcquMrAWg; webcodeuuid=5cfa4215-9333-45de-8118-bb834cb6c2e1; xfpcwebsiteesffddToken=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ4ZndlYmNvZGV1dWlkIjoiOTgxYWVhYjItYzFlNi00NGNkLTk5YTAtNzJhZGViY2FjMGI4IiwiaWF0IjoxNTMyMDUxMTQ1LCJleHAiOjE1MzI2NTU5NDV9.bm6k_Ts-u_rqJZXYtYcTCNc6VzTeTq8FLxIHnamC4Vs; xfwebcodeuuid=981aeab2-c1e6-44cd-99a0-72adebcac0b8; Hm_lvt_6711a956f9c03dac8b82dc27defd3b99=1531992805,1532053125,1532059852; webcomponentuuid=cfb82145-4bd1-41c4-9b86-1327ab7a8ac4; Hm_lpvt_6711a956f9c03dac8b82dc27defd3b99=1532059859; prev_pgn=%E6%88%90%E4%BA%A4%E9%A1%B5; _ha=1532059859471.7967483421',
           'Host': 'shenzhen.fangdd.com',
           'Referer': 'http://shenzhen.fangdd.com/chengjiao/',
           'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/66.0.3359.181 Chrome/66.0.3359.181 Safari/537.36'}

url = 'http://shenzhen.fangdd.com/chengjiao/907510.html'


def anal_page(text):
    l = leh(text)
    d = {
        'title': l.xpath('//div[@class="header-inner w clearfix"]/h1[@class="title"]/text()')[0].split('\n')[0],
        'trade_date':
            l.xpath('//div[@class="header-inner w clearfix"]/h1[@class="title"]/span[@class="deal-info"]/text()')[0],
        'total_price':
            l.xpath('//div[@class="basic-detail"]/div[@class="sell-box"]/p[@class="total-price"]/span/em/text()')[0],
        'average_price':
            l.xpath('//div[@class="basic-detail"]/div[@class="sell-box"]/p[@class="avr-price"]/span/em/text()')[0],
        'basic_detail': [l.xpath('//div[@class="basic-detail"]/ul[@class="h-around-list"]/li[' + str(i) + ']/text()')
                         for i in range(1, 7)]
    }
    d['trade_date'] = d['basic_detail'][0][0] if d['basic_detail'][0] else None
    d['region'] = d['basic_detail'][1][0] if d['basic_detail'][1] else None
    d['floor'] = re.sub('[\n ]', '', ''.join(d['basic_detail'][2])) if d['basic_detail'][2] else None
    d['face'] = d['basic_detail'][3][0] if d['basic_detail'][3] else None
    d['build_date'] = d['basic_detail'][4][0] if d['basic_detail'][4] else None
    d['type'] = d['basic_detail'][5][0] if d['basic_detail'][5] else None

    d.pop('basic_detail')
    return d


async def async_get(num_list):
    data = {}
    async with aiohttp.ClientSession() as session:
        for num in num_list:
            url = 'http://shenzhen.fangdd.com/chengjiao/%s.html' % (str(num))
            async with session.get(url, headers=headers) as resp:
                if resp.status < 400:
                    try:
                        data[num] = anal_page(await resp.text())
                    except KeyboardInterrupt:
                        break
                    except:
                        data[num]={}
                else:
                    data[num] = {}
    return data

loop = asyncio.get_event_loop()
def downloads(num_list):
    res = loop.run_until_complete(async_get(num_list))
    return res


while True:
    t0=time.time()
    dic = {i['_id']: i for i in col.find({'times': 0, 'lock': 0}).limit(200)}
    t1=time.time()
    col.update_many({'_id': {'$in': list(dic.keys())}}, {'$set': {'lock': 1}})
    t2=time.time()
    try:
        data = downloads(list(dic.keys()))
    except KeyboardInterrupt:
        break
    except Exception as e:
        print(e)
    t3=time.time()
    for i in data:
        data[i]['times'] = dic[i]['times']+1
        data[i]['lock'] = 0
        col.update_one({'_id':i},{'$set':data[i]})
    t4=time.time()
    print(t1-t0,t2-t1,t3-t2,t4-t3,t4-t0,len(data))
