class Price_predictor():
    def predict(self,address,face,area,structure,floor,total_floor):
        price_predicted=0
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