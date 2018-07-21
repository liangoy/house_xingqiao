import config
import requests
from utils import gaode
import json
from utils.fts import async_http


class Gaode_service():
    key = config.GAODE_KEY

    def add_sign(self, par):
        par['key'] = self.key
        par['sign'] = gaode.encrypt(par=par, key=self.key)
        return par

    def address2location(self, address_list=None, city=None, batch='false', output='JSON', concurrent=1):
        par_list = []
        url = 'http://restapi.amap.com/v3/geocode/geo?parameters'
        for address in address_list:
            par = {
                'address': address,
                'batch': batch,
                'output': output,
            }
            par = self.add_sign(par)
            par_list.append(par
        )
        resp_list = async_http.get([{'url': url, 'params': par} for par in par_list])

        data = []
        for i, j in zip(resp_list, par_list):
            resp_json = json.loads(i['content'].decode())
            d = {
                'address': j['address'],
                'formatted_address': resp_json['geocodes'][0]['formatted_address'],
                'location': resp_json['geocodes'][0]['location']
            }
            data.append(d)
        return data

    def around(self, key_words=None, location=None, radius='3000', types=None, sortrule='distance', output='JSON'):
        url = 'http://restapi.amap.com/v3/place/around?parameters'
        par_list = []
        for key_word in key_words.split(','):
            par = {
                'keywords': key_word,
                'location': location,
                'sortrule': sortrule,
                'radius': radius,
                'output': output,
                'offset': '20',
                'page': '1',
                'types': types
            }
            for i in list(par.keys()):
                if par[i] == None:
                    par.pop(i)

            par = self.add_sign(par)
            par_list.append(par)

        resp_list = async_http.get([{'url': url, 'params': par} for par in par_list])

        data = {}
        for i, j in zip(resp_list, par_list):
            data[j['keywords']] = json.loads(i['content'].decode())['count']
        return data


gaode_service = Gaode_service()
if __name__ == '__main__':
    from pprint import pprint

    # gs = Gaode_service()
    addr = ['漳州市华安县靖河路37号8栋']
    # addr = '漳州市华安县华丰中学,华安县湖滨花园'
    # addr='深圳市光明新区公明光明大道光明1号'
    # addr='广东省深圳市南山区南油南光路65-22号'
    # addr = '深圳南山华侨城沙河东路186号深圳湾畔花园D栋8091厨2室1阳台1卫1厅|广东省-深圳市-深圳湾畔花园-1厨2室1阳台1卫1厅'
    pprint(gaode_service.address2location(address_list=addr))
    # pprint(gs.around(location=gs.address2location(address=addr)[1],key_words='学校,银行'))
    # loop = asyncio.get_event_loop()
    # import time
    # s=time.time()
    # async def get(n):
    #     async with aiohttp.ClientSession() as session:
    #         for i in range(n):
    #             async with session.get('http://www.baidu.com') as resp:
    #                 print(len(await resp.text()))
    # loop.run_until_complete(asyncio.wait([get(10)]))
    # loop.close()
    # e=time.time()
    # print(e - s)
    # for i in range(10):
    #     print(len(requests.get('http://baidu.com').text))
    # e1=time.time()
    #
    # print(e1-e)
