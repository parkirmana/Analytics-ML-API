import os
import datetime
import pytz
from math import floor
from PIL import Image

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

# API that returns complete detection and update/insert database response
@app.route('/image', methods=['POST', 'GET'])
def get_image():
    if request.method == 'POST':
        # Unpack request
        image = request.files["images"]
        IMAGE_REQUEST = image.filename
        image.save(os.path.join(os.getcwd(), 'detections', IMAGE_REQUEST))
        IMAGE_PATH = os.path.join(os.getcwd(), 'detections', IMAGE_REQUEST)
        place = dict(request.form)["place"]

        # Detect license plate object
        img = cv2.imread(IMAGE_PATH)
        IMAGE_CROPPED = obj_detection.detect(img)
        img_crop = Image.fromarray(IMAGE_CROPPED)
        img_crop.save(os.path.join(os.getcwd(), 'detections', "crop_"+IMAGE_REQUEST))

        # Detect digit license plate
        image_np = np.array(IMAGE_CROPPED)

        input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
        detections = digits_detection.detect(input_tensor)
        digit_plate = digits_detection.get_digits_lpr(detections)
        # digit_plate = 'AE1941E'

        # Filter query to database
        vehicle = db.session.query(Vehicle).filter_by(plate_number=digit_plate).scalar()

        # Check is there user with plate number = digit_plate
        if (vehicle is not None):
            # Check whether user has booked parking slot
            booking = db.session.query(Booking).filter_by(id_user=vehicle.id_user, id_vehicle=vehicle.id_vehicle, status='BOOKED').scalar()
            # BOOKED
            if (booking is not None):
                booking.status = 'DONE'
                db.session.commit()

            parking_place = db.session.query(Universities).filter_by(name=place).scalar()
            transaction = db.session.query(Transaction).filter_by(id_user=vehicle.id_user, id_vehicle=vehicle.id_vehicle, id_place=parking_place.id_place, is_done=False).scalar()
            
            # Check whether IN or OUT
            # OUT
            if (transaction is not None):
                try:
                    # Update time_out in transaction
                    time_out = datetime.datetime.now(pytz.UTC)
                    transaction.time_out = time_out
                    transaction.is_done = True
                    db.session.commit()

                    # Generate notification and response data
                    time_in = transaction.time_in
                    time_out = transaction.time_out
                    time_diff = (time_out - time_in).total_seconds()

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
                        "timein": str(time_in),
                        "timeout": str(time_out),
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
                        "time_in": str(time_in),
                        "time_out": str(time_out),
                    }

                    send_notification(notif_data)

                    print("update transaction succeeded")
                    return render_template('parking.html', data=data)
                except:
                    time_in = transaction.time_in
                    data = {
                        "response": "update transaction failed",
                        "id_user": transaction.id_user,
                        "id_parking": transaction.id_parking,
                        "plate_number": digit_plate,
                        "place": place,
                        "time_in": time_in.strftime("%H:%M:%S"),
                    }
                    print("update transaction failed")
                    return render_template('parking.html', data=data)
            
            # IN
            # Case 1 : the user has made a transaction before (there is transaction record with is_done = True)
            # Case 2 : the user has never made a transaction before (transaction is None)
            else:
                try:
                    # Add new transaction
                    t = datetime.datetime.now(pytz.UTC)
                    new_transaction = Transaction(id_user=vehicle.id_user, id_vehicle=vehicle.id_vehicle, id_place=parking_place.id_place, time_in=t)
                    db.session.add(new_transaction)
                    db.session.commit()

                    # Generate notification and response data
                    time_in = new_transaction.time_in

                    # Query select device_token
                    device_token = db.session.query(User.device_token).filter_by(id_user=vehicle.id_user).scalar()

                    # Sent post to android
                    notif_data = json.dumps({
                        "to" : "{}".format(device_token),
                        "data" : {
                        "body": "You are entering {} parking lot!".format(place),
                        "title":"You are going in",
                        "timein": str(time_in),
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
                        "id_user": new_transaction.id_user,
                        "id_parking": new_transaction.id_parking,
                        "plate_number": digit_plate,
                        "place": place,
                        "time_in": str(time_in),
                        "time_out": str(new_transaction.time_out),
                    }

                    send_notification(notif_data)

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

        # User not found
        else:
            data = {
                "response": "user not found",
                "plate_number": digit_plate
            }
            print("user not found")
            return render_template('parking.html', data=data)

    else:
        return render_template('index.html')

# API that returns predicted digit plate number only
@app.route('/predict', methods=['POST'])
def get_prediction():
    if request.method == 'POST':
        # Unpack request
        image = request.files["images"]
        IMAGE_REQUEST = image.filename
        image.save(os.path.join(os.getcwd(), 'detections', IMAGE_REQUEST))
        IMAGE_PATH = os.path.join(os.getcwd(), 'detections', IMAGE_REQUEST)

        # Detect license plate object
        img = cv2.imread(IMAGE_PATH)
        try:
            IMAGE_CROPPED = obj_detection.detect(img)

            # Detect digit license plate
            image_np = np.array(IMAGE_CROPPED)

            input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
            detections = digits_detection.detect(input_tensor)
            digit_plate = digits_detection.get_digits_lpr(detections)

            data = {
                'response': 'plate number detected',
                'plate_number': digit_plate
            }

            return jsonify(data), 200
        except:
            data = {
                'response': 'failed detect plate number'
            }
            return jsonify(data), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
