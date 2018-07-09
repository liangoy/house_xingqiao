from services.gaode import gaode_service
from services.predict import price_predictor

def location(**kwargs):
    address=kwargs['address']
    address,location=gaode_service.address2location(address=address)
    return {'address':address,'location':location}

def price_predicted(**kwargs):
    return {'price_predicted':"0",'influnce':kwargs}