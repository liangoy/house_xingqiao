import math
import numpy as np
import socket

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


if __name__=='__main__':
    dis=distance((117.542204,24.999849),(117.522364,25.009424))
    print(dis)