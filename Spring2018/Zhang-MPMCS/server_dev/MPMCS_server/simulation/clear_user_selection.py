from pymongo import MongoClient
us_dbs = [ 'us1','us2', 'us3']
simu_dbs = ['simulationDB1','simulationDB2']
dbs = simu_dbs
for db in dbs:
    client = MongoClient('mongodb://username:password@ip_address/' + db, port_number)
    mydb = client[db]
    mydb.Tasks.delete_many({})
    ids = list(mydb.Users.find({}))
    for uid in ids:
        mydb.Users.update_one({'_id': uid['_id']},{'$set': {'selected_times': 0}}, upsert=True)

