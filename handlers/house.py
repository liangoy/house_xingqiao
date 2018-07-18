from services.gaode import gaode_service
from services.predict import price_predictor
from utils import fts
import config
from copy import deepcopy
import numpy as np


def location(**kwargs):
    address = kwargs['address']
    if ',' not in address:
        addr_list = [address]
    else:
        addr_list = address.split(',')
    addr_list = addr_list[:200]
    return gaode_service.address2location(address_list=addr_list)


def distance(**kwargs):
    location1 = kwargs['location1']
    location2 = kwargs['location2']
    location1 = [float(i) for i in location1.split(',')]
    location2 = [float(i) for i in location2.split(',')]
    return str(fts.distance(location1, location2))


def average_rental_price(**kwargs):
    location = kwargs['location']
    radius = float(kwargs['radius'])
    no_less_than = int(kwargs['no_less_than'])

    location = [float(i) for i in location.split(',')]
    loc = [[float(i) for i in j.split(',')] for j in config.HOUSE_RENT.location]
    dis = [fts.distance(location, i) for i in loc]
    price = list(config.HOUSE_RENT.price / config.HOUSE_RENT.area)
    dis_price = list(zip(dis, price))
    dis_price = sorted(dis_price, key=lambda x: x[0])
    dis_price = [i for i in dis_price if i[0] < radius][1:]
    if len(dis_price) >= no_less_than:
        return np.mean([i[1] for i in dis_price])
    else:
        return '房屋数量少于no_less_than', 401


def average_selling_price(**kwargs):
    location = kwargs['location']
    radius = float(kwargs['radius'])
    no_less_than = int(kwargs['no_less_than'])

    location = [float(i) for i in location.split(',')]
    loc = [[float(i) for i in j.split(',')] for j in config.HOUSE_SALE.location]
    dis = [fts.distance(location, i) for i in loc]
    price = list(config.HOUSE_SALE.price)
    dis_price = list(zip(dis, price))
    dis_price = sorted(dis_price, key=lambda x: x[0])
    dis_price = [i for i in dis_price if i[0] < radius][1:]
    if len(dis_price) >= no_less_than:
        return np.mean([i[1] for i in dis_price])
    else:
        return '房屋数量少于no_less_than', 401


def rental_price_predicted(**kwargs):
    area = kwargs['area']
    year = kwargs['year']
    rooms = kwargs['rooms']
    wc = kwargs['wcs']
    living_rooms = kwargs['living_rooms']
    floor_type = kwargs['floor_type']
    total_floors = kwargs['total_floor']
    face = kwargs['face']
    decoration = kwargs['decoration']
    address = kwargs['address']

    location = gaode_service.address2location(address_list=[address])[0]['location']
    around = gaode_service.around(key_words='银行,学校,医院,宾馆,公交站,地铁站', location=location, radius=500)
    bus_stop, hospital, subway_station, school, hotel, bank = around['公交站'], around['医院'], around['地铁站'], around['学校'], \
                                                              around['宾馆'], around['银行']
    arp = average_rental_price(location=location, radius=500, no_less_than=5)
    asp = average_selling_price(location=location, radius=500, no_less_than=5)

    if len(arp) > 1 or len(asp) > 1:
        return '地区过于偏僻', 402

    par = [area, year, rooms, living_rooms, wc, total_floors, bus_stop, hospital, subway_station, school, hotel, bank,
           arp, asp, face, decoration, floor_type]
    return price_predictor.predict_selling_price(*par)


def selling_price_predicted(**kwargs):
    area = kwargs['area']
    year = kwargs['year']
    rooms = kwargs['rooms']
    wc = kwargs['wcs']
    living_rooms = kwargs['living_rooms']
    floor_type = kwargs['floor_type']
    total_floors = kwargs['total_floor']
    face = kwargs['face']
    decoration = kwargs['decoration']
    address = kwargs['address']

    location = gaode_service.address2location(address_list=[address])[0]['location']
    around = gaode_service.around(key_words='银行,学校,医院,宾馆,公交站,地铁站', location=location, radius=500)
    bus_stop, hospital, subway_station, school, hotel, bank = around['公交站'], around['医院'], around['地铁站'], around['学校'], \
                                                              around['宾馆'], around['银行']
    arp = average_rental_price(location=location, radius=500, no_less_than=5)
    asp = average_selling_price(location=location, radius=500, no_less_than=5)

    if type(asp) == tuple or type(arp) == tuple:
        return '地区过于偏僻,找不到周围房子的均价', 402

    par = [area, year, rooms, living_rooms, wc, total_floors, bus_stop, hospital, subway_station, school, hotel, bank,
           arp, asp, face, decoration, floor_type]
    price_predicted = price_predictor.predict_selling_price(*par)

    area_par = [deepcopy(par) for i in range(180)]
    for i, j in enumerate(area_par):
        j[0] = 20 + i
    year_par = [deepcopy(par) for i in range(30)]
    for i, j in enumerate(year_par):
        j[1] = 1988 + i
    rooms_par = [deepcopy(par) for i in range(6)]
    for i, j in enumerate(rooms_par):
        j[2] = 0 + i
    living_rooms_par = [deepcopy(par) for i in range(4)]
    for i, j in enumerate(living_rooms_par):
        j[3] = 0 + i
    wc_par = [deepcopy(par) for i in range(4)]
    for i, j in enumerate(wc_par):
        j[4] = 0 + i
    total_floors_par = [deepcopy(par) for i in range(40)]
    for i, j in enumerate(total_floors_par):
        j[5] = 0 + i
    face_par = [deepcopy(par) for i in range(8)]
    for i, j in enumerate(face_par):
        j[-3] = 0 + i
    decoration_par = [deepcopy(par) for i in range(4)]
    for i, j in enumerate(decoration_par):
        j[-2] = 0 + i
    floor_type_par = [deepcopy(par) for i in range(4)]
    for i, j in enumerate(floor_type_par):
        j[-1] = 0 + i

    influence = {
        'area': price_predicted - np.mean([float(price_predictor.predict_selling_price(*i)) for i in area_par]),
        'year': price_predicted - np.mean([float(price_predictor.predict_selling_price(*i)) for i in year_par]),
        'rooms': price_predicted - np.mean([float(price_predictor.predict_selling_price(*i)) for i in rooms_par]),
        'living_rooms': price_predicted - np.mean(
            [float(price_predictor.predict_selling_price(*i)) for i in living_rooms_par]),
        'wc': price_predicted - np.mean([float(price_predictor.predict_selling_price(*i)) for i in wc_par]),
        'total_floors': price_predicted - np.mean(
            [float(price_predictor.predict_selling_price(*i)) for i in total_floors_par]),
        'face': price_predicted - np.mean([float(price_predictor.predict_selling_price(*i)) for i in face_par]),
        'decoration': price_predicted - np.mean(
            [float(price_predictor.predict_selling_price(*i)) for i in decoration_par]),
        'floor_type': price_predicted - np.mean(
            [float(price_predictor.predict_selling_price(*i)) for i in floor_type_par]),
    }

    return {'price_predicted': str(price_predicted), 'influence': influence}


def around_info(**kwargs):
    location = kwargs['location']
    radius = kwargs['radius']
    info = gaode_service.around(key_words='银行,学校,医院,宾馆,公交站,地铁站', location=location, radius=radius)
    for i in info:
        info[i] = str(info[i])
    return info


if __name__ == '__main__':
    print(len(average_selling_price(**{'location': '1,1', 'radius': '500', 'no_less_than': '5'})))
