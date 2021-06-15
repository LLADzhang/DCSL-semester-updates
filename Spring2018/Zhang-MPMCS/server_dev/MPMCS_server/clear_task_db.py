from pymongo import MongoClient
us_dbs = [ 'db1','db2', 'db3']
for db in us_dbs:
    client = MongoClient('mongodb://username:password@ip_address/' + db, db_port)
    mydb = client[db]
    mydb.Tasks.delete_many({})

