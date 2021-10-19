from app import db

class Vehicle(db.Model):
    __tablename__ = 'user_vehicles'

    id_user = db.Column(db.Integer, primary_key=True)
    id_vehicle = db.Column(db.Integer)
    plat_number = db.Column(db.String(10))
    vehicle_type = db.Column(db.String(8))
    last_parking = db.Column(db.DateTime(timezone=True))

    def __init__(self, id_vehicle, id_user, plat_number, vehicle_type, last_parking):
        self.id_vehicle = id_vehicle
        self.id_user = id_user
        self.plat_number = plat_number
        self.vehicle_type = vehicle_type
        self.last_parking = last_parking

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

class Booking(db.Model):
    __tablename__ = 'bookings'

    id_booking = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer)
    id_vehicle = db.Column(db.Integer)
    id_place = db.Column(db.Integer)
    time_booking = db.Column(db.DateTime(timezone=True))
    status = db.Column(db.String(10))

    def __init__(self, id_user, id_vehicle, id_place, time_booking, status):
        self.id_user = id_user
        self.id_vehicle = id_vehicle
        self.id_place = id_place
        self.time_booking = time_booking
        self.status = status
    
    def __repr__(self) -> str:
        return '<Booking -- id_user: {} id_booking: {} id_place: {} time_boking: {}>'.format(self.id_user, self.id_booking, self.id_place, self.time_booking)

    def serialize(self):
        return {
            'id_user': self.id_user,
            'id_booking': self.id_booking,
            'id_vehicle': self.id_vehicle,
            'id_place': self.id_place,
            'time_booking': self.time_booking,
            'status': self.status
        }

class Place(db.Model):
    __tablename__ = 'places'

    id_place = db.Column(db.Integer, primary_key=True)
    id_company = db.Column(db.Integer)
    name = db.Column(db.String(32))
    address = db.Column(db.String(64))
    coordinate = db.Column(db.ARRAY(db.String(32)))

    def __repr__(self) -> str:
        return '<Place -- id_place: {} id_company: {} name: {}>'.format(self.id_place, self.id_company, self.name)

    def serialize(self):
        return {
            'id_place': self.id_place,
            'id_company': self.id_company,
            'name': self.name,
            'address': self.address,
            'coordinate': self.coordinate,
        }

class Transaction(db.Model):
    __tablename__ = 'uni_parking_transactions'

    id_user = db.Column(db.Integer)
    id_transaction = db.Column(db.Integer, primary_key=True)
    id_vehicle = db.Column(db.Integer)
    id_place = db.Column(db.Integer)
    time_in = db.Column(db.DateTime(timezone=True))
    time_out = db.Column(db.DateTime(timezone=True))
    is_done = db.Column(db.Boolean())

    def __init__(self, id_user, id_vehicle, id_place, time_in, is_done=False):
        self.id_user = id_user
        self.id_vehicle = id_vehicle
        self.id_place = id_place
        self.time_in = time_in
        self.is_done = is_done

    def __repr__(self) -> str:
        return '<Transactions -- id_user: {} id_transaction: {} time_in: {}>'.format(self.id_user, self.id_transaction, self.time_in)

    def serialize(self):
        return {
            'id_user': self.id_user,
            'id_transaction': self.id_transaction,
            'id_vehicle': self.id_vehicle,
            'id_place': self.id_place,
            'time_in': self.time_in,
            'time_out': self.time_out,
            'isDone': self.is_done
        }

class User(db.Model):
    __tablename__ = 'users'

    id_user = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(64))
    phone_number = db.Column(db.String(12))
    email = db.Column(db.String(64))
    password = db.Column(db.String(64))
    verification_pin = db.Column(db.String(64))
    device_token = db.Column(db.String(180))


    def __init__(self, id_user, full_name, phone_number, email, password, verification_pin, device_token):
        self.id_user = id_user
        self.full_name = full_name
        self.phone_number = phone_number
        self.email = email
        self.password = password
        self.verification_pin = verification_pin
        self.device_token = device_token

    def __repr__(self) -> str:
        return '<User -- id_user: {} device_token: {}>'.format(self.id_user, self.device_token)

    def serialize(self):
        return {
            'id_user': self.id_user,
            'full_name': self.full_name,
            'phone_number': self.phone_number,
            'email': self.email,
            'password': self.password,
            'verification_pin': self.verification_pin,
            'device_token': self.device_token
        }