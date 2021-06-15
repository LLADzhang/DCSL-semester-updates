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
    allBuildings = {'corec':[40.428692, -86.922263],
                'pmu':[40.425251, -86.910770],
                'ece':[40.428763, -86.911911],
                'cs':[40.427889, -86.916892],
                'elliot':[40.427950, -86.914854],
                'beering':[40.425684, -86.916221],
                'earhart':[40.425770, -86.924363],
                'shealy':[40.426179, -86.920655],
                'chauncey':[40.423525, -86.907669]
                }

    if buildingName not in allBuildings.keys():
        if "/" in buildingName:
            latitude = float(buildingName.split('/')[0])
            longitude = float(buildingName.split('/')[1])
            return [latitude, longitude]
    else:
        return allBuildings[buildingName]

def finish_dumping(port):
    try:
        conn = HTTPConnection(ip_address, port)
        conn.request("POST", "/", body=json.dumps({"content":"newTaskInserted"}))
    except:
        traceback.print_exc()

def dumpToDb(results, db):
    print("dubmping " + str(results))
    client = MongoClient('mongodb://username:password@id/' + db, port)
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
    start = start.replace(month = Month, day=Day, year=Year, tzinfo=datetime.timezone.utc)

    totalMins = (datetime.datetime.strptime(results["endTime"], '%H:%M') - datetime.datetime.strptime(results["startTime"], '%H:%M')).total_seconds() / 60
    period = int(results["period"])
    num_requests = int(totalMins / period)

    print(str(num_requests) + " requests")
    for i in range(num_requests):
        outputTime = start + datetime.timedelta(minutes=(tolerance / 60/ 1000/2 + period * i))
        epoch =datetime.datetime.utcfromtimestamp(0).replace(tzinfo=datetime.timezone.utc)
        outputData["time"] = ((outputTime - epoch).total_seconds()+18000) * 1000
        outputData["_id"] = taskID
        outputData["assigned"] = False
        outputData["finished"] = False
        outputData["assignment_list"] = []
        TaskCollection.insert_one(outputData)
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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # task task_file and generate many. DO NOT PUT DUPLICATE TASKs.
        # location+date+startTime+endTime+period+tolerance+sensors+num_devices+radius
        # sample line in the file looks like:
        # ee+2017/06/04+14:00+18:00+20+30+magnetic/pressure+5+100
        with open(sys.argv[1], "r") as inputFile:
            lines = inputFile.readlines()
        for line in lines:
            results = parse_task(line)
            if results != None:
                dumpToDb(results, "us1")
                dumpToDb(results, "us2")
                dumpToDb(results, "us3")
    else:
        results = {}
        location = input("where you want to task to happen? [corec, pmu, ece, cs] ")
        while location != "pmu" and location != "ece" and location != "corec" and location != "cs":
            pp("this place is not logged in our system")
            location = input("where you want to task to happen? [corec, pmu, ece, cs] ")
        results["location"] = location

        date = input("What date? e.g. 06/04 --> month/day ")
        while not dateCheck(date):
            date = input("What date? e.g. 06/04 --> month/day ")
        year = str(datetime.datetime.now().year) + "/"
        date = year + date
        results["date"] = date

        startTime = input("when to start? [24 hour format] e.g. 14:00 ")
        while not timeCheck(startTime):
            startTime = input("when to start? [24 hour format] e.g. 14:00 ")
        results["startTime"] = startTime

        endTime = input("when to end?  e.g. 15:00 ")
        while not timeCheck(endTime):
            endTime = input("when to end?  e.g. 15:00 ")
        results["endTime"] = endTime

        period = input("what is the priodicity [m]? e.g. 20 ")
        while not re.match(r"^[0-9]+$", period):
            pp("task numer is not recoginized")
            period = input("what is the priodicity [m]? e.g. 20 ")
        results["period"] = period

        tolerance = input("how many minutes tolerant? e.g. 20 ")
        while not re.match(r"^[0-9]+$", tolerance):
            pp("task numer is not recoginized")
            tolerance = input("how many minutes tolerant? e.g. 20 ")
        results["tolerance"] = tolerance

        sensors = input("what sensors? " + str(Sensor_List) + " e.g. magnetic/pressure ")
        while not sensorCheck(sensors):
            sensors = input("what sensors? " + Sensor_List + " e.g. magnetic/pressure ")
        results["sensors"] = sensors

        num_devices = input("how many users? e.g. 10 ")
        while not re.match(r"^[0-9]+$", num_devices):
            pp("task number is not recoginized")
            num_devices = input("how many users? e.g. 10 ")
        results["num_devices"] = num_devices

        radius = input ("what radius[m]? e.g. 100 ")
        while not re.match(r"^[0-9]+$", num_devices):
            pp("radius is not recoginized")
            radius = input ("what radius[m]? e.g. 100 ")
        results["radius"] = radius

        dumpToDb(results, "us1")
        dumpToDb(results, "us2")
        dumpToDb(results, "us3")

    time.sleep(5)
    finish_dumping(8000)
    finish_dumping(8001)
    finish_dumping(8002)



