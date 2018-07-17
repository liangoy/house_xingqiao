import xgboost as xgb
import config
import requests
class Price_predictor():
    sale_model=xgb.Booster(model_file=config.MODEL_SALE_XGB)

    def predict_selling_price(self,address,face,area,structure,floor,total_floor):
        requests.get()



        [area,year,rooms,living_rooms,wc,total_floors,bus_stop,hospital,subway_station,school,hotel,bank,average_rental_price,average_selling_price,'face','decoration','floor_type']
        ['area', 'year', 'rooms', 'living_rooms', 'wc', 'total_floors', 'bus_stop', 'hospital', 'subway_station',
         'school', 'hotel', 'bank', 'average_rental_price', 'average_selling_price', 'label', 0, 1, 2, 3, 4, 5, 6, 7, 8,
         9, 10, 11, 12, 13, 14, 15]


        price_predicted=self.sale_model.predict()
        influence={
            'address':0,
            'face':0,
            'area':0,
            'romms':0,
            'living_rooms':0,
            'floor':0,
            'total_floor':0
        }
        return price_predicted,influence

price_predictor=Price_predictor()