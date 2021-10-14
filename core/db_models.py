from app import db

class Vehicle(db.Model):
    __tablename__ = 'user_vehicle'

    id_user = db.Column(db.Integer, primary_key=True)
    id_vehicle = db.Column(db.Integer)
    plate_number = db.Column(db.String(8))
    car_type = db.Column(db.String(8))
    img_stnk = db.Column(db.String(64))

    def __init__(self, id_vehicle, id_user, plate_number, car_type, img_stnk):
        self.id_vehicle = id_vehicle
        self.id_user = id_user
        self.plate_number = plate_number
        self.car_type = car_type
        self.img_stnk = img_stnk

    def __repr__(self) -> str:
        return '<Vehicle -- id_user: {} id_vehicle: {}>'.format(self.id_user, self.id_vehicle)

    def serialize(self):
        return {
            'id_vehicle': self.id_vehicle,
            'id_user': self.id_user,
            'plate_number': self.plate_number,
            'car_type': self.car_type,
            'img_stnk': self.img_stnk,
        }

class Transaction(db.Model):
    __tablename__ = 'parking_transactions'

    id_user = db.Column(db.Integer)
    id_transaction = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(8), unique=True)
    place = db.Column(db.String(64))
    time_enter = db.Column(db.DateTime(timezone=True))
    time_out = db.Column(db.DateTime(timezone=True))
    price = db.Column(db.Numeric())
    isDone = db.Column(db.Boolean())

    def __init__(self, id_user, plate_number, place, time_enter, isDone=False):
        self.id_user = id_user
        self.plate_number = plate_number
        self.place = place
        self.time_enter = time_enter
        self.isDone = isDone

    def __repr__(self) -> str:
        return '<Vehicle -- id_user: {} id_transaction: {} time_enter: {}>'.format(self.id_user, self.id_transaction, self.time_enter)

    def serialize(self):
        return {
            'id_user': self.id_user,
            'id_transaction': self.id_transaction,
            'plate_number': self.plate_number,
            'place': self.place,
            'time_enter': self.time_enter,
            'time_out': self.time_out,
            'price': self.price,
            'isDone': self.isDone
        }

class Device(db.Model):
    __tablename__ = 'user_device'

    id_user = db.Column(db.Integer, primary_key=True)
    device_token = db.Column(db.String(256))


    def __init__(self, id_user, device_token):
        self.id_user = id_user
        self.device_token = device_token

    def __repr__(self) -> str:
        return '<Device -- id_user: {} device_token: {}>'.format(self.id_user, self.device_token)

    def serialize(self):
        return {
            'id_user': self.id_user,
            'device_token': self.device_token
        }