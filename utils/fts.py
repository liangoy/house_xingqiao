import math
import numpy as np
import socket
import aiohttp
import asyncio
import json

def distance(location1,location2):#eg:location1=(0,0),location2=(1,1)
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(math.radians, [location1[0], location1[1], location2[0], location2[1]])

    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371*10**3  # 地球平均半径，单位为米
    return c * r

def one_hot(lis):
    n=np.zeros([len(lis),max(lis)+1])
    for i,j in enumerate(lis):
        n[i,j]=1
    return n

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


class Async_http():
    loop=asyncio.get_event_loop()
    async def _async_http_get(self,params_list):
        data=[None]*len(params_list)
        async with aiohttp.ClientSession() as session:
            for index,par in enumerate(params_list):
                async with session.get(**par) as resp:
                    data[index] = {
                        'status_code':resp.status,
                        'content':await resp.read()
                    }
        return data
    def get(self,params_list):
        resp=self.loop.run_until_complete(self._async_http_get(params_list))
        return resp

async_http=Async_http()


if __name__=='__main__':
    resp=async_http.get([{'url':'http://baidu.com','headers':{}},{'url':'http://baidu.com'}])
    print(resp)