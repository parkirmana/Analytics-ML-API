import os
import json
import sys

FCM_URL = 'your-fcm-url'
AUTH_KEY = 'your-auth-key'
DEVICE_KEY = 'your-device-key'

def send_notification(notif_data):
    
    command = 'curl -X POST -H "Authorization: {}" -H "Content-Type: application/json" -d \'{}\' {}'.format(AUTH_KEY, notif_data, FCM_URL)
    print(command)
    os.system(command)

# code for testing
if __name__ == '__main__':
    mode = sys.argv[1]

    time_enter = "02:09:430"
    time_out = "03:39:450"
    duration = "24h 45m 450s"
    place = "Rumah Anna"
    price = "Rp 35.000.000"

    notif_data = json.dumps({
        "to" : "{}".format(DEVICE_KEY),
        "data" : {
        "body": "Please pay the parking fare!",
        "title":"You are going out",
        "timein": time_enter,
        "timeout": time_out,
        "totaltime": duration,
        "fare": price,
        "location": place
        },
        "notification": {
        "body": "Please pay the parking fare!",
        "title": "You are going out",
        "click_action": "com.dicoding.nextparking.ui.payment.PaymentActivity"
        }
        })

    if mode == 'command-line':
        send_notification(notif_data)
    else:
        print("wrong argument")