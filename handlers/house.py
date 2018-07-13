from services.gaode import gaode_service
from services.predict import price_predictor
from utils import fts
import config
import numpy as np


def location(**kwargs):
    address = kwargs['address']
    return gaode_service.address2location(address=address)


def distance(**kwargs):
    location1 = kwargs['location1']
    location2 = kwargs['location2']
    location1 = [float(i) for i in location1.split(',')]
    location2 = [float(i) for i in location2.split(',')]
    return str(fts.distance(location1, location2))


def price_predicted(**kwargs):
    return {'price_predicted': "0", 'influnce': kwargs}


def around_info(**kwargs):
    location = kwargs['location']
    radius = kwargs['radius']
    info=gaode_service.around(key_words='银行,学校,医院,宾馆,公交站,地铁站',location=location,radius=radius)
    for i in info:
        info[i] = str(info[i])
    return info


def average_price(**kwargs):
    location = kwargs['location']
    radius = float(kwargs['radius'])
    no_less_than = int(kwargs['no_less_than'])

    location = [float(i) for i in location.split(',')]
    loc = [[float(i) for i in j.split(',')] for j in config.HOUSE_DF.location]
    dis = [fts.distance(location, i) for i in loc]
    price = list(config.HOUSE_DF.price / config.HOUSE_DF.area)
    dis_price = list(zip(dis, price))
    dis_price = sorted(dis_price, key=lambda x: x[0])
    dis_price = [i for i in dis_price if i[0] < radius][1:]
    if len(dis_price) >= no_less_than:
        return np.mean([i[1] for i in dis_price])
    else:
        return '房屋数量少于no_less_than', 401
