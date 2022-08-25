import time
from loguru import logger
from pyzbar.pyzbar import decode
import cv2
import pymongo
from datetime import datetime
import yaml

with open('config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

cap = cv2.VideoCapture(1)
logger.add('video_recognizer_errors', retention='1 minute', level='ERROR')


def activate_ticket(ticket_id, activation_date):
    try:
        pymongo_conn = pymongo.MongoClient(config['mongo'])
        db = pymongo_conn.test
        collection = db.orders
        ticket = collection.find({'tickets._id': ticket_id})
        collection.update_one({'tickets._id': ticket_id},
                              {"$set": {"tickets.$.activationDate": activation_date}})
        collection.update_one({'tickets._id': ticket_id},
                              {"$set": {"tickets.$.status": "activated"}})
    except pymongo.errors.ServerSelectionTimeoutError as error:
        logger.error(error)


def qr_recognition():
    while True:
        ret, frame = cap.read()
        cv2.imshow('Video QR', frame)
        if decode(frame):
            order_id = decode(frame)[0].data.decode('utf-8')
            date = datetime.now()
            activate_ticket(order_id, date)
            print('ok')
            time.sleep(10)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    qr_recognition()