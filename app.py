import os
import datetime
from math import ceil, floor

import cv2
import numpy as np
import tensorflow as tf

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
# Import YOLO
from core.YOLO import yolo_model
# Import TFOD
from core.TFOD import tfod_model
# Import method to send request to android
from core.notification import send_notification


from flask import Flask, request, Response, jsonify, send_from_directory, abort, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
import json

# Initialize Flask application
app = Flask(__name__)

# Parking price per hours
LOW_PRICE = 3000
HIGH_PRICE = 5000

# Database configuration
from core.db_config import DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_NAME
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret-key'

db = SQLAlchemy(app)

# Import database models
from core.db_models import *

# Load YOLOv4 model
yolo_labels_path = "obj.names"
yolo_cfg_path = "yolov4-plate-detector.cfg"
yolo_weights_path = "yolov4-plate-detector_best.weights"
obj_detection = yolo_model(yolo_labels_path, yolo_cfg_path, yolo_weights_path)

# Load TFOD model
tfod_labels_path = "workspace/annotations/label_map.pbtxt"
tfod_cfg_path = "workspace/models/efficientdet_d1_coco17/pipeline.config"
tfod_ckpt_path = "workspace/models/efficientdet_d1_coco17/ckpt-6"
digits_detection = tfod_model(tfod_labels_path, tfod_cfg_path, tfod_ckpt_path)

# API that returns image with detections on it
@app.route('/image', methods=['POST', 'GET'])
def get_image():
    if request.method == 'POST':
        # Unpack request
        image = request.files["images"]
        IMAGE_REQUEST = image.filename
        image.save(os.path.join(os.getcwd(), 'detections', 'tmp', IMAGE_REQUEST))
        IMAGE_PATH = os.path.join(os.getcwd(), 'detections', 'tmp', IMAGE_REQUEST)
        place = dict(request.form)["place"]

        # category_index = label_map_util.create_category_index_from_labelmap('./Tensorflow/annotations/label_map.pbtxt')

        # Detect license plate object
        img = cv2.imread(IMAGE_PATH)
        IMAGE_CROPPED = obj_detection.detect(img)

        # Detect digit license plate
        image_np = np.array(IMAGE_CROPPED)

        input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
        detections = digits_detection.detect(input_tensor)
        digit_plate = digits_detection.get_digits_lpr(detections)

        # Filter query to database
        vehicle = db.session.query(Vehicle).filter_by(plate_number=digit_plate).scalar()
        transaction = db.session.query(Transaction).filter_by(plate_number=digit_plate, place=place, isDone=False).scalar()

        # If user with plate_number <digit_plate> parking at <place> --> want to quit parking lot
        if (vehicle is not None) and (transaction is not None):
            try:
                # Add time_out
                transaction.time_out = datetime.datetime.now().time()
                db.session.commit()

                # Add parking fee
                time_enter = datetime.datetime.combine(datetime.date.today(), transaction.time_enter)
                time_out = datetime.datetime.combine(datetime.date.today(), transaction.time_out)
                time_diff = (time_out - time_enter).total_seconds()
                time_diff_in_hours = time_diff/3600
                if time_diff_in_hours < 1:
                    transaction.price = LOW_PRICE
                else:
                    transaction.price = ceil(time_diff_in_hours) * HIGH_PRICE
                db.session.commit()

                time_enter = transaction.time_enter
                time_out = transaction.time_out
                price = transaction.price
                hours = floor(time_diff/3600)
                minutes = floor((time_diff%3600)/60)
                seconds = floor(time_diff%60)

                # Query select device_token
                device_token = db.session.query(Device.device_token).filter_by(id_user=vehicle.id_user).scalar()

                # Sent post to android
                notif_data = json.dumps({
                    "to" : "{}".format(device_token),
                    "data" : {
                    "body": "Please pay the parking fare!",
                    "title":"You are going out",
                    "timein": time_enter.strftime("%H:%M:%S"),
                    "timeout": time_out.strftime("%H:%M:%S"),
                    "totaltime": "{}h {}m {}s".format(hours, minutes, seconds),
                    "fare": "{}".format(price),
                    "location": place
                    },
                    "notification": {
                    "body": "Please pay the parking fare!",
                    "title": "You are going out",
                    "click_action": "com.dicoding.nextparking.ui.payment.PaymentActivity"
                    }
                })

                send_notification(notif_data)

                data = {
                    "response": "update transaction succeeded",
                    "id_user": transaction.id_user,
                    "id_transaction": transaction.id_transaction,
                    "plate_number": transaction.plate_number,
                    "place": transaction.place,
                    "time_enter": time_enter.strftime("%H:%M:%S"),
                    "time_out": time_out.strftime("%H:%M:%S"),
                    "price": str(transaction.price)
                }

                print("update transaction succeeded")
                return render_template('parking.html', data=data)
            except:
                data = {
                    "response": "update transaction failed",
                    "id_user": transaction.id_user,
                    "id_transaction": transaction.id_transaction,
                    "plate_number": transaction.plate_number,
                    "place": transaction.place,
                    "time_enter": time_enter.strftime("%H:%M:%S"),
                }
                print("update transaction failed")
                return render_template('parking.html', data=data)

        # If user with plate_number <digit_plate> is exist and want to parking at <place>
        elif (vehicle is not None):
            try:
                # Add new transaction
                print(datetime.datetime.now().time())
                new_transaction = Transaction(id_user=vehicle.id_user, plate_number=vehicle.plate_number, place=place, time_enter=datetime.datetime.now().time())
                db.session.add(new_transaction)
                db.session.commit()

                time_enter = new_transaction.time_enter

                # Query select device_token
                device_token = db.session.query(Device.device_token).filter_by(id_user=vehicle.id_user).scalar()

                # Sent post to android
                notif_data = json.dumps({
                    "to" : "{}".format(device_token),
                    "data" : {
                    "body": "You are entering {} parking lot!".format(place),
                    "title":"You are going in",
                    "timein": time_enter.strftime("%H:%M:%S"),
                    "location": place
                    },
                    "notification": {
                    "body": "You are entering {} parking lot!".format(place),
                    "title":"You are going in",
                    "click_action": "com.dicoding.nextparking.HomeActivity"
                    }
                })

                send_notification(notif_data)

                data = {
                    "response": "add new transaction record succeed",            
                    "id_user": new_transaction.id_user,
                    "id_transaction": new_transaction.id_transaction,
                    "plate_number": new_transaction.plate_number,
                    "place": new_transaction.place,
                    "time_enter": time_enter.strftime("%H:%M:%S"),
                    "time_out": str(new_transaction.time_out),
                    "price": str(new_transaction.price)
                }
                print("Add new record succeded")
                return render_template('parking.html', data=data)
            except:
                data = {
                    "response": "add new transaction record failed",
                    "id_user": vehicle.id_user,
                    "plate_number": digit_plate
                }
                print("add new transaction record failed")
                return render_template('parking.html', data=data)

        # If user not found
        else:
            data = {
                "response": "user not found",
                "plate_number": digit_plate
            }
            print("user not found")
            return render_template('parking.html', data=data)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
