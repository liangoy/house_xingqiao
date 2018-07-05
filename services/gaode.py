import config
import requests
from utils import gaode
class Gaode_service():
    key=config.GAODE_KEY
    def add_sign(self,par):
        par['key']=self.key
        par['sign'] = gaode.encrypt(par=par, key=self.key)
        return par
    def address2location(self,address=None,city=None,batch='false',output='JSON',callback=None):
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

    def around(self,key_word=None,location=None,radius='3000',types = None,sortrule='distance',output='JSON'):
        url='http://restapi.amap.com/v3/place/around?parameters'
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
        for i in par:
            if par[i]==None:
                par.pop(i)

        par = self.add_sign(par)
        r = requests.get(url, params=par)
        r.close()
        res = r.json()
        return res['count']

gaode_service=Gaode_service()
if __name__=='__main__':
    from pprint import pprint
    gs=Gaode_service()
    addr='深圳南山华侨城沙河东路186号深圳湾畔花园D栋8091厨2室1阳台1卫1厅|广东省-深圳市-深圳湾畔花园-1厨2室1阳台1卫1厅'
    pprint(gs.address2location(address=addr))
    pprint(gs.around(location=gs.address2location(address=addr)[1],key_word='地铁',types='交通设施服务'))