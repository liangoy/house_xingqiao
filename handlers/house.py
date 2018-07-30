from services.gaode import gaode_service
from services.predict import price_predictor
from utils import fts
import config
from copy import deepcopy
import numpy as np
import time


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

    longitude, latitude = tuple([float(i) for i in location.split(',')])
    det = 0.002248304014796826/250*float(radius)
    df = config.HOUSE_SALE
    ap=df[(longitude - det < df.longitude) & (df.longitude < longitude + det) & (latitude - det < df.latitude) & (
                df.latitude < latitude + det)].average_price
    if len(ap) >= no_less_than:
        return ap.mean()
    else:
        return '房屋数量少于no_less_than', 401


def average_selling_price(**kwargs):
    location = kwargs['location']
    radius = float(kwargs['radius'])
    no_less_than = int(kwargs['no_less_than'])

    longitude, latitude = tuple([float(i) for i in location.split(',')])
    det = 0.002248304014796826/250*float(radius)
    df = config.HOUSE_SALE
    ap=df[(longitude - det < df.longitude) & (df.longitude < longitude + det) & (latitude - det < df.latitude) & (
                df.latitude < latitude + det)].average_price
    if len(ap) >= no_less_than:
        return ap.mean()
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
    area = float(kwargs['area'])
    build_date = float(kwargs['build_date'])
    trade_date = '2018-07'
    rooms = kwargs['rooms']
    wcs = kwargs['wcs']
    living_rooms = kwargs['living_rooms']
    floor_type = kwargs['floor_type']
    total_floor = kwargs['total_floor']
    face = kwargs['face']
    decoration = kwargs['decoration']
    address = kwargs['address']

    location = gaode_service.address2location(address_list=[address])[0]['location']
    longitude, latitude = location.split(',')
    around = gaode_service.around(key_words='银行,学校,医院,宾馆,公交站,地铁站', location=location, radius=500)
    bus_stop, hospital, subway_station, school, hotel, bank = around['公交站'], around['医院'], around['地铁站'], around['学校'], \
                                                              around['宾馆'], around['银行']
    around_price = average_selling_price(location=location, radius=250, no_less_than=20)

    if type(around_price) == tuple:
        return '地区过于偏僻,找不到周围房子的均价', 402

    par = {
        'longitude': longitude,
        'latitude': latitude,
        "area": area,
        "build_date": build_date,
        "trade_date": time.mktime(tuple([int(i) for i in (trade_date + '-01-01').split('-')[:3]]) + (0, 0, 0, 0, 0, 0)),
        "rooms": rooms,
        "living_rooms": living_rooms,
        # "wcs": wcs,
        "total_floor": total_floor,
        "bus_stop": bus_stop,
        "hospital": hospital,
        "subway_station": subway_station,
        "school": school,
        "hotel": hotel,
        "bank": bank,
        "around_price": around_price,
        "face": face,
        # "decoration": decoration,
        "floor_type": floor_type,
    }
    price_predicted = price_predictor.predict_selling_price(**par)

    area_par = [deepcopy(par) for i in range(180)]
    for i, j in enumerate(area_par):
        j['area'] = 20 + i
    build_date_par = [deepcopy(par) for i in range(30)]
    for i, j in enumerate(build_date_par):
        j['build_date'] = 1988 + i
    rooms_par = [deepcopy(par) for i in range(6)]
    for i, j in enumerate(rooms_par):
        j['rooms'] = 0 + i
    living_rooms_par = [deepcopy(par) for i in range(4)]
    for i, j in enumerate(living_rooms_par):
        j['living_rooms'] = 0 + i
    wcs_par = [deepcopy(par) for i in range(4)]
    for i, j in enumerate(wcs_par):
        j['wcs'] = 0 + i
    floor_type_par = [deepcopy(par) for i in range(6)]
    for i, j in enumerate(floor_type_par):
        j['floor_type'] = 0 + i
    total_floor_par = [deepcopy(par) for i in range(40)]
    for i, j in enumerate(total_floor_par):
        j['total_floor'] = 0 + i
    face_par = [deepcopy(par) for i in range(11)]
    for i, j in enumerate(face_par):
        j['face'] = 0 + i
    # decoration_par = [deepcopy(par) for i in range(4)]
    # for i, j in enumerate(decoration_par):
    #     j['decoration'] = 0 + i
    floor_type_par = [deepcopy(par) for i in range(4)]
    for i, j in enumerate(floor_type_par):
        j['floor_type'] = 0 + i

    influence = {
        'area': price_predicted - np.mean([float(price_predictor.predict_selling_price(**i)) for i in area_par]),
        'build_date': price_predicted - np.mean(
            [float(price_predictor.predict_selling_price(**i)) for i in build_date_par]),
        'rooms': price_predicted - np.mean([float(price_predictor.predict_selling_price(**i)) for i in rooms_par]),
        'living_rooms': price_predicted - np.mean(
            [float(price_predictor.predict_selling_price(**i)) for i in living_rooms_par]),
        # 'wc': price_predicted - np.mean([float(price_predictor.predict_selling_price(**i)) for i in wcs_par]),
        'total_floor': price_predicted - np.mean(
            [float(price_predictor.predict_selling_price(**i)) for i in total_floor_par]),
        'face': price_predicted - np.mean([float(price_predictor.predict_selling_price(**i)) for i in face_par]),
        # 'decoration': price_predicted - np.mean(
        #     [float(price_predictor.predict_selling_price(**i)) for i in decoration_par]),
        'floor_type': price_predicted - np.mean(
            [float(price_predictor.predict_selling_price(**i)) for i in floor_type_par]),
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
    print(selling_price_predicted(area=90, build_date=1990, trade_date='2018', rooms=3, living_rooms=2, wcs=1, face=1,
                                  total_floor=30, floor_type=4, decoration=1, address='南山区'))
