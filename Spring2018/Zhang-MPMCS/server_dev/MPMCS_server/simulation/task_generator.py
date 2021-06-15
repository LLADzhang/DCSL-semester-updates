from pymongo import MongoClient
import sys
from Sensor import  Sensor_List, Sensor_Map
from http.client import HTTPConnection
from pprint import pprint as pp
# the client db reference
import re
import datetime
import json
import time
import traceback



def dateCheck(date):
    correct = True
    try:
        datetime.datetime.strptime(date, '%m/%d')
    except ValueError:
        pp("Incorrect data format, should be MM_DD_YYYY")
        correct = False

    return correct
def timeCheck(Time):
    correct = True
    try:
        time.strptime(Time, '%H:%M')
    except ValueError:
        pp("Incorrect time format, should be hh/mm")
        correct = False

    return correct


def sensorCheck(sensors):
    for sensor in sensors.split("/"):
        if sensor not in Sensor_List:
            return  False
    return True


def getLocation(buildingName):
    allBuildings = {'corec':[40.4288505,-86.9214604], 'pmu':[40.4248517,-86.9114363], 'ece':[40.4285349,-86.9124526], 'cs':[40.4276277,-86.9169919]}
    if buildingName not in allBuildings.keys():
        if "/" in buildingName:
            latitude = float(buildingName.split('/')[0])
            longitude = float(buildingName.split('/')[1])
            return [latitude, longitude]
    else:
        return allBuildings[buildingName]

def finish_dumping(port):
    try:
        offset =  0 * 60 * 60 * 1000
        conn = HTTPConnection("localhost", port)
        conn.request("POST", "/", body=json.dumps({"content":"newTaskInserted", "cur_time": 1518469200000 - offset}))
        print("notify port:", port)
    except:
        traceback.print_exc()

def dumpToDb(results, db):
    print("dubmping " + str(results))
    client = MongoClient('mongodb://username:password@ip_address/' + db, port_number)
    db = client[db]
    TaskCollection = db['Tasks']
    taskID = 0
    for latest in TaskCollection.find({}, {"_id":1}).sort([("_id",-1)]).limit(1):
    # print(TaskCollection.find().count())
        print(latest)
        if latest:
            taskID = latest["_id"]+1
        else:
            taskID = 0
    sensors = [Sensor_Map[sen] for sen in sorted(results["sensors"].split("/"))]

    tolerance = int(results["tolerance"]) * 60 * 1000
    radius = int(results["radius"])
    location = getLocation(results["location"]) # an array [lat, lon] --> [float, float]
    num_devices = int(results["num_devices"])
    outputData={"tolerance": tolerance, "radius":radius, "location":location, "results":{}, "num_devices":num_devices, "sensors":sensors}
    # split task to requests
    date = results["date"]
    Year = int(date.split("/")[0])
    Month = int(date.split("/")[1])
    Day = int(date.split("/")[2])
    start = datetime.datetime.strptime(results["startTime"], '%H:%M')
    print("Month: {}, Day: {}, Year: {}".format(Month, Day, Year))
    start = start.replace(month = Month, day=Day, year=Year, tzinfo=datetime.timezone.utc)

    totalMins = (datetime.datetime.strptime(results["endTime"], '%H:%M') - datetime.datetime.strptime(results["startTime"], '%H:%M')).total_seconds() / 60
    period = int(results["period"])
    num_requests = int(totalMins / period)

    print(str(num_requests) + " requests")
    for i in range(num_requests):
        print(start)
        outputTime = start + datetime.timedelta(minutes=(tolerance / 60/ 1000/2 + period * i))
        print('outputTime: {}'.format(outputTime))
        epoch =datetime.datetime.utcfromtimestamp(0).replace(tzinfo=datetime.timezone.utc)
        outputData["time"] = ((outputTime - epoch).total_seconds()+18000) * 1000
        outputData["_id"] = taskID
        outputData["assigned"] = False
        outputData["finished"] = False
        outputData["assignment_list"] = []
        TaskCollection.insert_one(outputData)
        print(outputData)
        taskID+=1
    client.close()




def parse_task(task_string):
    if task_string[0] != '#':
        print(task_string)
        fields = task_string.split("+")
        if len(fields) != 9:
            print(task_string + " does not follow format")
            return None
        else:
            results ={}
            results["location"] = fields[0]
            results["date"] = fields[1]
            results["startTime"] = fields[2]
            results["endTime"] = fields[3]
            results["period"] = fields[4]
            results["tolerance"] = fields[5]
            results["sensors"] = fields[6]
            results["num_devices"] = fields[7]
            results["radius"] = fields[8].strip()

        return results
    else:
        return None




