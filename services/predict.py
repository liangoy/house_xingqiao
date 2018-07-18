import xgboost as xgb
import config

class Price_predictor():
    sale_model=xgb.Booster(model_file=config.MODEL_SALE_XGB)

    def predict_selling_price(self,area,year,rooms,living_rooms,wc,total_floors,bus_stop,hospital,subway_station,school,hotel,bank,average_rental_price,average_selling_price,face,decoration,floor_type):

        par=[area,year,rooms,living_rooms,wc,total_floors,bus_stop,hospital,subway_station,school,hotel,bank,average_rental_price,average_selling_price]

        face_one_hot = [0] * 8
        face_one_hot[int(face)]=1
        decoration_one_hot = [0] * 4
        decoration_one_hot[int(decoration)]=1
        floor_type_one_hot = [0] * 4
        floor_type_one_hot[int(floor_type)]=1

        par=par+face_one_hot+decoration_one_hot+floor_type_one_hot

        print(par)

        par=[[int(i)for i in par]]

        data=xgb.DMatrix(par)
        price_predicted = self.sale_model.predict(data)[0]
        return price_predicted

price_predictor=Price_predictor()

if __name__=='__main__':
    par=[50,2008,3,5,1,10,5,1,1,5,20,20,5000,50000,3,2,3]
    print(price_predictor.predict_selling_price(*par))