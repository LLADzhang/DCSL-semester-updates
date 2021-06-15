from http.client import HTTPConnection
from json import load, dumps, loads
from task_generator import parse_task, dumpToDb, finish_dumping
from sys import argv


def load_json_from_file(filename):
    return load(open(filename))

# def send_to_collector(message):
#      try:
#         collector_connection.request("POST", '/', body=dumps({'data':message}))
#         collector_connection.getresponse()
#      finally:
#         collector_connection.close()

def add_task(task):
    task = loads(task)
    results = parse_task(task['task'])

    if 'asa' in protocol:
        dumpToDb(results, 'simulationDB1')
    else:
        dumpToDb(results, 'simulationDB2')

ASA_SCHEDULER_SERVER = 8010
SA_SCHEDULER_SERVER = 8012
# REPLY_SERVER = 8090
# COLLECTOR_SERVER_PORT = 8083
# simu_reply_connection = HTTPConnection("128.46.73.216", REPLY_SERVER)
# collector_connection = HTTPConnection("128.46.73.216", COLLECTOR_SERVER_PORT)
if len(argv) < 2:
    exit(0)
protocol = argv[1]
for line in load_json_from_file("simulator.json"):
    #print(line)

    # if "status" in line:
    #     send_to_collector(dumps(line))
    if "task" in line:
        add_task(dumps(line))
    # else:
    #     try:
    #         simu_reply_connection.request("POST", "/", body=dumps(line))
    #         simu_reply_connection.getresponse()
    #     except:
    #         print('asa_reply_server is closed')
if 'asa' in protocol:
    finish_dumping(ASA_SCHEDULER_SERVER)
else:
    finish_dumping(SA_SCHEDULER_SERVER)
