import config
import requests
import grequests
from utils import gaode
import json
class Gaode_service():
    key=config.GAODE_KEY
    def add_sign(self,par):
        par['key']=self.key
        par['sign'] = gaode.encrypt(par=par, key=self.key)
        return par
    def address2location(self,address=None,city=None,batch='false',output='JSON',concurrent=1):
        url='http://restapi.amap.com/v3/geocode/geo?parameters'
        par={
            'address':address,
            'batch':batch,
            'output':output,
        }
        par=self.add_sign(par)
        r=requests.get(url,params=par)
        r.close()
        res=r.json()
        return res['geocodes'][0]['formatted_address'],res['geocodes'][0]['location']

    def around(self,key_words=None,location=None,radius='3000',types = None,sortrule='distance',output='JSON'):
        url='http://restapi.amap.com/v3/place/around?parameters'
        par_list=[]
        for key_word in key_words.split(','):
            par={
                'keywords':key_word,
                'location':location,
                'sortrule':sortrule,
                'radius':radius,
                'output':output,
                'offset':'20',
                'page':'1',
                'types':types
            }
            for i in list(par.keys()):
                if par[i]==None:
                    par.pop(i)

            par = self.add_sign(par)
            par_list.append(par)
        tasks=[grequests.get(url,params=i) for i in par_list]
        resp=list(zip(key_words.split(','),grequests.map(tasks)))
        for r in resp:
            r[1].close()
        return {i[0]:json.loads(i[1].text)['count'] for i in resp}


gaode_service=Gaode_service()
if __name__=='__main__':
    from pprint import pprint
    gs=Gaode_service()
    #addr='漳州市华安县靖河路37号8栋'
    addr='漳州市华安县华丰中学'
    #addr='深圳市光明新区公明光明大道光明1号'
    #addr='广东省深圳市南山区南油南光路65-22号'
    #addr = '深圳南山华侨城沙河东路186号深圳湾畔花园D栋8091厨2室1阳台1卫1厅|广东省-深圳市-深圳湾畔花园-1厨2室1阳台1卫1厅'
    pprint(gs.address2location(address=addr))
    pprint(gs.around(location=gs.address2location(address=addr)[1],key_words='学校'))