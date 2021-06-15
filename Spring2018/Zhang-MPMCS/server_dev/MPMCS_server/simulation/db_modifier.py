from pymongo import MongoClient
from sys import argv

if len(argv) < 2:
    print('Usage: dbname')
    exit(0)

db = argv[1]

client = MongoClient('mongodb://username:password@ip_address/' + db, port_number)
locations = client[db]['NewLocationCollection']

cur = locations.find()
for entry in cur:

    locations.update({'_id': entry['_id']}, {'$set':{'location_mongo': {'type': 'Point', 'coordinates': entry['location'][::-1]}}})
    #print(locations.find_one({'_id': entry['_id']}))
    #break
