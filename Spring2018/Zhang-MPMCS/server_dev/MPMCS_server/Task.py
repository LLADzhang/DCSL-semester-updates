import traceback
from geopy.distance import vincenty
from Utils import SECOND, MINUTE, update_device_scores, send_message, \
    current_milli_time, users, tasks, mylogger, locations, db
from Device import Device

class Task:
    # sensors passed in are a list
    # task id stored in database
    def __init__(self, my_kwarg):
        try:
            if my_kwarg:
                self.id = my_kwarg["_id"]
                # datetime converted to int. e.g Deadline is 10 am, tolerance is 10 mins. self.time = 10.05
                self.time = my_kwarg["time"]
                self.tolerance = my_kwarg["tolerance"]
                self.latitude = my_kwarg["location"][0]
                self.longitude = my_kwarg["location"][1]
                self.radius = my_kwarg["radius"]
                self.num_devices = my_kwarg["num_devices"]
                # sorted list in alphabetical order
                self.sensors = sorted(my_kwarg["sensors"], key=str.lower)
                self.results = my_kwarg.get("results")
                self.finished = my_kwarg.get("finished", False)
                self.assigned = my_kwarg.get("assigned", False)
                self.assignment_list = my_kwarg.get("assignment_list", [])  # both assignment_list and potential_devices are list of devices ids
                self.potential_devices = my_kwarg.get("potential_devices", [])
                self.waiting_pool = my_kwarg.get("waiting_pool", [])
                self.compromised = my_kwarg.get("compromised", False)
                self.reassigned = my_kwarg.get("reassigned", False)
        except KeyError:
            traceback.print_exc()

    @staticmethod
    def from_db(tid):
        res = tasks.find_one({'_id': tid})
        return Task(res)

    def to_json(self, device_id):
        return {
            'id': self.id,
            'deviceId': device_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'radius': self.radius,
            'sensors': self.sensors,
            'deadline': self.time + self.tolerance / 2
        }


    def find_nearby_devices(self, need_immediate_number):
        mylogger.info('Immediate need '+ str(need_immediate_number) + " devices for task " + str(self.id))
        cur_time = current_milli_time()
        nearby_idss = locations.find({
            "timeStamp": {"$gte": cur_time - 15 * MINUTE, "$lte": cur_time}
        })
        nearby_idsss = [x['uid'] for x in nearby_idss if vincenty(x['location'], (self.latitude, self.longitude)).meters  <  self.radius]
        mylogger.info("found " + str(nearby_idsss))
        nearby_ids = list(set(nearby_idsss) - set(self.assignment_list) - set(self.waiting_pool))
        mylogger.info("after elimination" + str(nearby_ids))
        device_list = []
        for device_id in nearby_ids:
            loc = list(locations.find({"uid": device_id, "location": {"$ne": [0, 0]}}).sort("timeStamp", -1).limit(1))[0]['location']
            bat = db.Batteries.find_one({"_id": device_id})
            user = db.Users.find_one({'_id': device_id})
            token = user.get('token', '')
            selected_time = user.get('selected_times', 0)
            if token != '':
                device_list.append(Device(id=device_id, latitude=loc[0], longitude=loc[1],
                                              bat_level=float(bat["level"]), bat_status=bat["status"], selected_times=selected_time, token=token))

        if len(device_list) > need_immediate_number:
            return list(sorted(update_device_scores(device_list), key=lambda d: d.score)[:need_immediate_number])
        else:
            return device_list



    def send_to_devices(self, devices):

        task_dic = tasks.find_one({"_id": self.id}, {"waiting_pool" : 1, "assignment_list": 1})
        self.assignment_list = task_dic["assignment_list"]
        self.waiting_pool = task_dic.get("waiting_pool", [])
        cur_time  = current_milli_time()
        need_immediate = 0
        tokens = []
        for device in devices:
            loc_list = list(locations.find({"uid": device.id, "location": {"$ne": [0, 0]},
                                                               "timeStamp": {"$gte": cur_time - 15 * MINUTE, "$lte": cur_time}
                                                               }).sort("timeStamp", -1).limit(1))
            if loc_list:
                current_device_location = loc_list[0]['location']
            else:
                current_device_location = []
            if current_device_location:
                mylogger.info('try assigning task ' + str(self.id)+ ' to '+ str(device.id))
                user = users.find_one({'_id': device.id})
                if vincenty(current_device_location, (self.latitude, self.longitude)).meters < self.radius:
                    users.update({'_id': device.id}, {'$inc': {'predictability': 1}}, upsert=True)
                    if 'token' in user and user['_id'] not in self.assignment_list and user['_id'] in self.waiting_pool:
                        #send_message(user["token"], self.to_json(device.id))
                        mylogger.info('assigned task' + str(self.id) +  ' to' + str(device.id))
                        self.assignment_list.append(device.id)
                        tokens.append((user['token'], device.id))
                        self.waiting_pool.remove(device.id)
                        users.update({'_id': device.id}, {'$inc': {'selected_times': 1}}, upsert=True)
                    else:
                        mylogger.info("something wrong when assigning task "+ str(self.id) + " to device " + str(device.id))
                        mylogger.info("Device info: " + str(device))
                        mylogger.info("Task info " + str(self))
                        if device.id in self.assignment_list and device.id in self.waiting_pool:
                            mylogger.info("removed duplicate entries in waiting pool and assignment list device : " + str(device.id))
                            self.waiting_pool.remove(device.id)
                else:
                    mylogger.info("device " + str(device.id) + " is no longer in task region, removed from waiting pool")
                    mylogger.info("the distance is " + str(
                        vincenty(current_device_location, (self.latitude, self.longitude)).meters
                    ) + " radius is " + str(self.radius))
                    users.update({'_id': device.id}, {'$inc': {'unpredictability': 1}}, upsert=True)
                    if device.id in self.assignment_list:
                        self.assignment_list.remove(device.id)
                    if device.id in self.waiting_pool:
                        self.waiting_pool.remove(device.id)
                    need_immediate += 1
            else:
                need_immediate += 1
                self.waiting_pool.remove(device.id)
                mylogger.info("Can't find the current location for " + str(device.id) + " removed from waiting pool")
                users.update({'_id': device.id}, {'$inc': {'unpredictability': 1}}, upsert=True)


        if need_immediate > 0:
            nearby_devices = self.find_nearby_devices(need_immediate)
            if len(nearby_devices) == 0:
                mylogger.info('Cannot find any nearby devices for task '+ str(self.id))
            for nearby_device in nearby_devices:
                tokens.append((nearby_device.token, device.id))
                
                mylogger.info('immediate assigned task ' + str(self.id) + ' to ' + str(nearby_device.id))
                self.assignment_list.append(nearby_device.id)
                if nearby_device.id in self.waiting_pool:
                    self.waiting_pool.remove(nearby_device.id)
                users.update({'_id': nearby_device.id}, {'$inc': {'selected_times': 1}}, upsert=True)

        if len(self.assignment_list) >= self.num_devices:
            self.assigned = True
            tasks.update({'_id': self.id}, {'$set': {'assigned': True}})
        if self.time + self.tolerance/2 < cur_time:
            tasks.update_one({"_id": self.id}, {'$set': {"compromised": True}})

        mylogger.info('current assignment list: ' + str(self.assignment_list))
        mylogger.info('current waiting  pool: ' + str(self.waiting_pool))
        tasks.update({'_id': self.id}, {'$set': {'assignment_list': self.assignment_list}})
        tasks.update({'_id': self.id}, {'$set': {'waiting_pool': self.waiting_pool}})
        for token, device_id in tokens: 
            send_message(token, self.to_json(device_id))

    def __str__(self):
        return "id: " + str(self.id) +\
               ", time: " + str(self.time) +\
               ", assignment_list: " + str(self.assignment_list) +\
               ", waiting_pool: " + str(self.waiting_pool) +\
               ", tolerance: " + str(self.tolerance) +\
               ", latitude: " + str(self.latitude) +\
               ", longitude: " + str(self.longitude) +\
               ", radius: " + str(self.radius) +\
               ", sensors: " + str(self.sensors)
