from services.gaode import gaode_service
from services.predict import price_predictor


def location(**kwargs):
    address = kwargs['address']
    address, location = gaode_service.address2location(address=address)
    return {'address': address, 'location': location}


def price_predicted(**kwargs):
    return {'price_predicted': "0", 'influnce': kwargs}


def around_info(**kwargs):
    location = kwargs['location']
    radius = kwargs['radius']
    info = {
        'banks': gaode_service.around(key_word='银行', location=location, radius=radius),
        'schools': gaode_service.around(key_word='学校', location=location, radius=radius),
        'hospitals': gaode_service.around(key_word='医院', location=location, radius=radius),
        'hotels': gaode_service.around(key_word='宾馆', location=location, radius=radius),
        'bus_stops': gaode_service.around(key_word='公交站', location=location, radius=radius),
        'subway_stations': gaode_service.around(key_word='地铁站', location=location, radius=radius),
    }
    for i in info:
        info[i] = str(info[i])
    return info
