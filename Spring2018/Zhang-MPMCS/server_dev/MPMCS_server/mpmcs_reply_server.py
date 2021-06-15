from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import logging
import json
from sys import argv, stdout, stderr
from pymongo import MongoClient

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
mylogger = logging.getLogger()
mylogger.setLevel(logging.INFO)

logPath = "./"
fileName = 'asa_reply_server'
fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
fileHandler.setFormatter(logFormatter)
fileHandler.setLevel(logging.INFO)
mylogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(stdout)
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.INFO)
mylogger.addHandler(consoleHandler)

errHandler = logging.StreamHandler(stderr)
errHandler.setFormatter(logFormatter)
errHandler.setLevel(logging.ERROR)
mylogger.addHandler(errHandler)

def update_credential(data_json):
    uid = str(data_json["deviceId"])
    token = str(data_json["token"])
    if "simulator" in token:
        client = MongoClient('mongodb://username:password@ip/simulationDB', portnumber)
        db = client['simulationDB']
    else:
        client = MongoClient('mongodb://username:password@ip/collection', portnumber)
        db = client['collection']

    userCollection = db['Users']
    userCollection.find_one_and_update({"_id":uid}, {"$set": {"token" : token}}, upsert=True)


def checkFinishStatus(taskId):
    client = MongoClient('mongodb://username:password@ip/collection', portnumber)
    db = client['collection']
    TaskCollection = db['Tasks']
    taskDic = TaskCollection.find_one({"_id":taskId}, {"results" : 1, "num_devices": 1})
    result = taskDic["results"]
    num_devices = taskDic["num_devices"]
    if len(result) == num_devices:
        TaskCollection.update({"_id":taskId}, {"$set": {"finished": True}})


def update_dataReply(data_json):
    # tid is task id
    if "error" in data_json.keys():
        return
    taskId = int(data_json["taskId"])
    sensors = data_json["sensors"]
    uid = data_json['deviceId']
    client = MongoClient('mongodb://username:password@ip/collection', portnumber)
    db = client['collection']
    TaskCollection = db['Tasks']
    taskDic= TaskCollection.find_one({"_id":taskId}, {"results" : 1, "assignment_list":1})
    if taskDic:
        mylogger.info(str(taskDic))
    else:
        exit(1)
    # TODO: rewrite the result part
    # {'id': '0', 'UID': '867686022614778', 'sensors': {'TYPE_PRESSURE': [0], 'TYPE_MAGNETIC': [10.625, 19.8125, -29.9375]}, 'latitude': 40.42881105, 'longitude': -86.91255899}
    result = taskDic.get("results")
    assignmentList = taskDic.get("assignment_list")
    # result: a dictionary. key = uid, value = {sensor1: [float, float, float], sensor2: [float, float, float]}
    if uid in assignmentList:
        userSensorsDic =  {} # the dic for each user, with key = sensor name and val = sensor values [float, float, float]
        mylogger.info('sensors: '+ str(sensors))
        for name, val in sensors.items():
            mylogger.info('name: ' + str(name)+ ' value: '+ str(val))
            #name is the name of sensor
            # val is a list [float, float, float] of sensor values
            userSensorsDic[name] = val
        result[uid] = userSensorsDic
        TaskCollection.update({"_id":taskId}, {"$set": {"results": result}}, upsert=True)

        checkFinishStatus(taskId)
        mylogger.info("data reply finished")


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        return

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))
        return

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
        logging.info("TYPE: {}".format(type(post_data.decode('utf-8'))))
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))
        data_json = json.loads(post_data.decode('utf-8'))
        logging.info("JSON data {}".format(data_json))
        if "token" in data_json.keys():
            update_credential(data_json)
        else:
            update_dataReply(data_json)
        return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """handle requests in a separate thread."""


def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = ThreadedHTTPServer(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

def startServer():

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

startServer()
