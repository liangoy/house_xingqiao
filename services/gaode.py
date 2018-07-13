import config
import requests
from utils import gaode
import json
import aiohttp
import asyncio


class Gaode_service():
    key = config.GAODE_KEY
    loop = asyncio.get_event_loop()

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
            par_list.append(par)

        data = []
        async def get(pl):
            async with aiohttp.ClientSession() as session:
                for par in pl:
                    async with session.get(url, params=par) as resp:
                        resp_json = json.loads(await resp.text())
                        d = {
                            'address': par['address'],
                            'formatted_address': resp_json['geocodes'][0]['formatted_address'],
                            'location': resp_json['geocodes'][0]['location']
                        }
                        data.append(d)

        self.loop.run_until_complete(asyncio.wait([get(par_list)]))
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

        data = {}

        async def get(pl):
            async with aiohttp.ClientSession() as session:
                for par in pl:
                    async with session.get(url, params=par) as resp:
                        data[par['keywords']] = json.loads(await resp.text())['count']

        self.loop.run_until_complete(asyncio.wait([get(par_list)]))
        return data


gaode_service = Gaode_service()
if __name__ == '__main__':
    from pprint import pprint

    gs = Gaode_service()
    # addr='漳州市华安县靖河路37号8栋'
    addr = '漳州市华安县华丰中学,华安县湖滨花园'
    # addr='深圳市光明新区公明光明大道光明1号'
    # addr='广东省深圳市南山区南油南光路65-22号'
    # addr = '深圳南山华侨城沙河东路186号深圳湾畔花园D栋8091厨2室1阳台1卫1厅|广东省-深圳市-深圳湾畔花园-1厨2室1阳台1卫1厅'
    pprint(gs.address2location(address=addr))
    # pprint(gs.around(location=gs.address2location(address=addr)[1],key_words='学校,银行'))
