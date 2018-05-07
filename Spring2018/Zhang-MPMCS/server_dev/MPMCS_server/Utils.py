from threading import Timer
from pymongo import MongoClient
from Device import Device
from geopy.distance import vincenty
from gettime_ntp import gettime_ntp
from datetime import datetime
import logging, sys
from pyfcm import FCMNotification

SECOND = 1000
MINUTE = SECOND * 60
client = MongoClient('mongodb://username:password@db_ip_address/db_name', dbport)
db = client['db_name']
users = db.Users
tasks = db.Tasks
locations = db.NewLocationCollection

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
mylogger = logging.getLogger()
mylogger.setLevel(logging.INFO)

logPath = "./"
fileName = 'mpmcs_task_scheduler'
fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.INFO)
mylogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.INFO)
mylogger.addHandler(consoleHandler)

errHandler = logging.StreamHandler(sys.stderr)
errHandler.setFormatter(logFormatter)
errHandler.setLevel(logging.ERROR)
mylogger.addHandler(errHandler)


def send_message(regID, message):
    #  message by default should follow data-message
    push_service = FCMNotification(api_key="AIzaSyBGW1HeNME5HhFiw6YzS72bNFmlA8JOmDM")
    if "simulator" in regID:
        mylogger.info("send to " + str(regID) + " with " + str(message))
    else:
        return push_service.notify_single_device(registration_id=regID, data_message=message)


def current_milli_time():
    return int(gettime_ntp() * SECOND)
    # return int(round(time() * SECOND))


def calculate_device_score(device):
    if device.probability == 0:
        return float('inf')
    if device.unpredictability + device.predictability == 0:
        prediction_fraction = 0.5
    else:
        prediction_fraction = device.unpredictability/(device.unpredictability + device.predictability)
    return (0.4 * device.selected_times + 0.2 * (100 - device.bat_level) + 0.4 * device.tasksSatisfied + 0.2 * prediction_fraction) / device.probability


def update_device_scores(candidates):
    # run update_device_scores function
    for c in candidates:
        c.score = calculate_device_score(c)

    return candidates


def start_daemon(seconds, func, arguments):
    thread = Timer(seconds, func, arguments)
    thread.daemon = True
    thread.start()


def filter_devices_by_battery_level(devices, threshold=50):
    # input a list of devices within range
    return list(filter(lambda x: x.bat_level > threshold or x.bat_status == "Charging", devices))



def get_nearby_devices(task):
    cur_time = current_milli_time()
    nearby_idss = locations.find({
        "timeStamp": {"$gte": cur_time - 10 * MINUTE, "$lte": cur_time}
    })
    nearby_idsss = [x['uid'] for x in nearby_idss if vincenty(x['location'], (task.latitude, task.longitude)).meters < task.radius]

    mylogger.info("nearby users" + str(nearby_idsss))
    device_ids = list(set(nearby_idsss) - set(task.assignment_list) - set(task.waiting_pool))
    mylogger.info("after removing duplicates " + str(device_ids) + " stay")
    device_list = []
    for device_id in device_ids:

        loc = list(locations.find({"uid": device_id,
                               "location": {"$ne": [0, 0]},
                                            "timeStamp": {"$gte": cur_time - 10 * MINUTE, "$lte": cur_time}
                               }).sort("timeStamp", -1).limit(1))
        if loc:
            device_loc = loc[0]['location']
            if vincenty(device_loc, [task.latitude, task.longitude]).meters < task.radius:
                bat = db.Batteries.find_one({"_id": device_id})
                user = db.Users.find_one({'_id': device_id})
                token = user.get('token', '')
                selected_time = user.get('selected_times', 0)
                unpredictability = user.get('unpredictability', 0)
                if token != '':
                    device_list.append(Device(id=device_id, latitude=device_loc[0], longitude=device_loc[1],
                                              bat_level=float(bat["level"]), bat_status=bat["status"], selected_times=selected_time,
                                              token=token, unpredictability=unpredictability))

    return device_list


def get_potential_devices(task, radius, advance_min, cur_time):
    location = (task.latitude, task.longitude)
    mylogger.info("inteval to find devices are [" + str(cur_time - advance_min*MINUTE) + ", " + str(cur_time)+ "]" )

    device_idss = locations.find({
        "timeStamp": {"$gte": cur_time - advance_min * MINUTE, "$lte": cur_time}
    })
    device_idsss = [x['uid'] for x in device_idss if vincenty(x['location'], (task.latitude, task.longitude)).meters < radius]
    device_ids = list(set(device_idsss) - set(task.assignment_list) - set(task.waiting_pool))
    device_list = []
    for device_id in device_ids:
        loc = list(locations.find({"uid": device_id,
                               "location": {"$ne": [0, 0]},
                                            "timeStamp": {"$gte": cur_time - advance_min* MINUTE, "$lte": cur_time}
                               }).sort("timeStamp", -1).limit(1))
        if loc:
            device_loc = loc[0]['location']
            if vincenty(device_loc, location).meters < radius:
                bat = db.Batteries.find_one({"_id": device_id})
                user = db.Users.find_one({'_id': device_id})
                token = user.get('token', '')
                selected_time = user.get('selected_times', 0)
                if token != '':
                    device_list.append(Device(id=device_id, latitude=device_loc[0], longitude=device_loc[1],
                                              bat_level=float(bat["level"]), bat_status=bat["status"], selected_times=selected_time, token=token))

    return device_list

def milliseconds_to_string(milliseconds):
    return datetime.fromtimestamp(milliseconds/1000.0).strftime('%m-%d-%H:%M:%S')

def range_query(collection, center, radius, start_time, end_time, project=None):
    query = {
        'location_mongo': {
            '$nearSphere': {
                '$geometry': {
                    'type': 'Point',
                    'coordinates': center
                },
                '$maxDistance': radius
            }
        },
        'timeStamp': {
            '$gte': start_time,
            '$lte': end_time
        }
    }
    return collection.find(query) if project is None else collection.find(query, project)
