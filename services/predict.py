import xgboost as xgb
import config


class Price_predictor():
    sale_model = xgb.Booster(model_file=config.MODEL_SALE_XGB)

    def predict_selling_price(self, area, build_date, rooms, living_rooms, bus_stop, hospital,
                              subway_station, school, hotel, bank, face,total_floor,around_price,
                               floor_type, longitude, latitude, trade_date):
        par = {
            'area':float(area),
            'build_date':float(build_date),
            'rooms':int(rooms),
            'living_rooms':int(living_rooms),
            #'wcs':int(wcs),
            'bus_stop':int(bus_stop),
            'hospital':int(hospital),
            'subway_station':int(subway_station),
            'school':int(school),
            'hotel':int(hotel),
            'bank':int(bank),
            'longitude':float(longitude),
            'latitude':float(latitude),
            'trade_date':int(trade_date),
            'total_floor':int(total_floor),
            'around_price':float(around_price),
        }

        face_one_hot = [0] * 11
        face_one_hot[int(face)] = 1
        floor_type_one_hot = [0] * 5
        floor_type_one_hot[int(floor_type)] = 1

        par_list = [par[i] for i in sorted(par)] + face_one_hot + floor_type_one_hot

        data = xgb.DMatrix([par_list])
        price_predicted = self.sale_model.predict(data)[0]
        return price_predicted


price_predictor = Price_predictor()

if __name__ == '__main__':
    par = [10]*17
    print(price_predictor.predict_selling_price(*par))
