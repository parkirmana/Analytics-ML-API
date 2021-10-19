from app import db
import datetime
from db_models import *
from math import ceil, floor
import json

def update_timeout_transaction(transaction):
    transaction.time_out = datetime.datetime.now().time()
    db.session.commit()

def add_new_transaction(vehicle, parking_place):
    new_transaction = Transaction(id_user=vehicle.id_user, id_vehicle=vehicle.id_vehicle, id_place=parking_place.id_place, time_in=datetime.datetime.now().time())
    db.session.add(new_transaction)
    db.session.commit()

def gen_responses(transaction, vehicle, place, digit_plate, out):
    notif_data, data = '', ''

    if out:
        time_in = datetime.datetime.combine(datetime.date.today(), transaction.time_in)
        time_out = datetime.datetime.combine(datetime.date.today(), transaction.time_out)
        time_diff = (time_out - time_in).total_seconds()

        time_in = transaction.time_in
        time_out = transaction.time_out
        hours = floor(time_diff/3600)
        minutes = floor((time_diff%3600)/60)
        seconds = floor(time_diff%60)

        # Query select device_token
        device_token = db.session.query(User.device_token).filter_by(id_user=vehicle.id_user).scalar()

        # Notification data to android
        notif_data = json.dumps({
            "to" : "{}".format(device_token),
            "data" : {
            "body": "Please pay the parking fare!",
            "title":"You are going out",
            "timein": time_in.strftime("%H:%M:%S"),
            "timeout": time_out.strftime("%H:%M:%S"),
            "totaltime": "{}h {}m {}s".format(hours, minutes, seconds),
            "location": place
            },
            "notification": {
            "body": "Please pay the parking fare!",
            "title": "You are going out",
            "click_action": "com.dicoding.nextparking.ui.payment.PaymentActivity"
            }
        })

        # Response data
        data = {
            "response": "update transaction succeeded",
            "id_user": transaction.id_user,
            "id_parking": transaction.id_parking,
            "plate_number": digit_plate,
            "place": place,
            "time_enter": time_in.strftime("%H:%M:%S"),
            "time_out": time_out.strftime("%H:%M:%S"),
        }

    else:
        time_in = transaction.time_in

        # Query select device_token
        device_token = db.session.query(User.device_token).filter_by(id_user=vehicle.id_user).scalar()

        # Sent post to android
        notif_data = json.dumps({
            "to" : "{}".format(device_token),
            "data" : {
            "body": "You are entering {} parking lot!".format(place),
            "title":"You are going in",
            "timein": time_in.strftime("%H:%M:%S"),
            "location": place
            },
            "notification": {
            "body": "You are entering {} parking lot!".format(place),
            "title":"You are going in",
            "click_action": "com.dicoding.nextparking.HomeActivity"
            }
        })

        # Response data
        data = {
            "response": "add new transaction record succeed",            
            "id_user": transaction.id_user,
            "id_parking": transaction.id_parking,
            "plate_number": transaction.plate_number,
            "place": transaction.place,
            "time_enter": time_in.strftime("%H:%M:%S"),
            "time_out": str(transaction.time_out),
            "price": str(transaction.price)
        }
    
    return notif_data, data
