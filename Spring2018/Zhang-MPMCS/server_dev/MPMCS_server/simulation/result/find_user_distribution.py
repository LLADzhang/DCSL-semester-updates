from json import  load
from sys import argv
from pymongo import MongoClient
import gmplot
from geopy.distance import great_circle, vincenty

if len(argv) != 3:
    print("usage: xxxxx_task.json  which task want to analyze")
    exit(0)

polling_rate_file = argv[1]
task_id = int(argv[2])
tasks = load(open(polling_rate_file))

for task in tasks:
    if task["_id"] == task_id:
        # found the interested task
        task_time = task['time']
        tolerance = task['tolerance']
        task_loc = task['location']
        radius = task['radius']

client = MongoClient('mongodb://heng:hengdcsl@128.46.73.216/us1' , 27017)
db = client['us1']
locations = db['NewLocationCollection']

all_locations = list(locations.find({"location": {"$ne": [0, 0]}, "timeStamp": {"$gt": task_time - tolerance / 2, "$lt": task_time + tolerance / 2}}))
lats = []
longs = []

for loc in all_locations:
    lats.append(loc['location'][0])
    longs.append(loc['location'][1])
# print(lats, longs)
    if great_circle(loc['location'], task_loc).meters < radius:
        print("distance great_circle", great_circle(loc['location'], task_loc).meters)
        print("distance vincenty", vincenty(loc['location'], task_loc).meters)
        print("radius: ", radius)
        print(loc['location'], loc['timeStamp'])

gmap = gmplot.GoogleMapPlotter(lats[0], longs[0], 15)

gmap.scatter(lats, longs, 'cornflowerblue', edge_width=10)
gmap.circle(task_loc[0], task_loc[1], radius, color='#AA0000')
name = "task_"+ str(task_id) + "_maps.html"
gmap.draw(name)
