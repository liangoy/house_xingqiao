import requests
import hashlib
from functools import reduce

def encrypt(par=None,key=None):
    list_par=[str(i)+'='+str(par[i])for i in sorted(par)]
    string_par=reduce(lambda x,y:x+'&'+y,list_par)
    string_sign=hashlib.md5(string_par.encode()).hexdigest()
    return string_sign


if __name__=='__main__':
    print(encrypt({1:2},'234'))