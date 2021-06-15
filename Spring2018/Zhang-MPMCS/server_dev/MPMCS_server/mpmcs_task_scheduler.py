from Task import Task
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from mobility_prediction import path_model
from Utils import db, tasks, SECOND, MINUTE, update_device_scores, start_daemon, get_potential_devices, filter_devices_by_battery_level, current_milli_time,\
    milliseconds_to_string, mylogger, get_nearby_devices
import json


def assign_task(task, scored_candidates, cur_time, daemon=start_daemon):
    try:
        need_number = task.num_devices - len(task.assignment_list) - len(task.waiting_pool)
        if need_number > 0:
            if len(scored_candidates) >= need_number:
                devices = sorted(scored_candidates, key=lambda d: d.score)[:need_number]
                status = True
            else:
                devices = scored_candidates
                mylogger.info("WARNING: assigning task " + str(task.id) + ' is not finished, found ' + str(len(scored_candidates)) + ' devices '+ str(task.num_devices - len(scored_candidates)) + ' more are needed')
                status = False

            timer = (task.time - cur_time - task.tolerance / 2) / SECOND
            if timer > 0:
                mylogger.info("assigning  " + str(task.id) + " after " + str(timer) + " seconds to " + str(len(devices)) + ' devices')
                daemon(timer,  task.send_to_devices, [devices])
                for d in devices:
                    if d.id not in task.assignment_list and d.id not in task.waiting_pool:
                        task.waiting_pool.append(d.id)
                tasks.update({'_id': task.id}, {'$set': {'waiting_pool': task.waiting_pool}})
            else:
                if cur_time < task.time + task.tolerance / 2 :
                    #within window send right now
                    mylogger.info("schedule task " + str(task.id) + " within tolerance window")
                    daemon(5, task.send_to_devices, [devices])
                    for d in devices:
                        if d.id not in task.assignment_list and d.id not in task.waiting_pool:
                         task.waiting_pool.append(d.id)
                    mylogger.info("devices: " + str([d for d in task.waiting_pool]) + ' are waiting to be assigned')
                    tasks.update({'_id': task.id}, {'$set': {'waiting_pool': task.waiting_pool}})

                else:
                    mylogger.info("Too late to schedule " + str(task.id) )
                    status = False
                    tasks.update({'_id': task.id}, {'$set': {'waiting_pool': []}})
        else:
            mylogger.info("There are enough devices for task " + str(task.id)  + ". No need to assign to new devices.")
            mylogger.info("Assignment List is: " + str([d for d in task.assignment_list]))
            mylogger.info("waiting pool is: " + str([d for d in task.waiting_pool]))
            mylogger.info("candidates were going to assign but not necessary: " + str(scored_candidates))
            status = True
        return  status

    except Exception:
        traceback.print_exc()
        return False


def schedule_tasks(task_list, cur_time):
    # take in a list of Task objects
    un_finished_tasks = []
    for task in task_list:
        mylogger.info("\nscheduling " + str(task))
        potential_devices = get_potential_devices(task, radius=10 * task.radius, advance_min=15, cur_time=cur_time)
        mylogger.info("potentialDevices:")
        mylogger.info(str([str(d.id) for d in potential_devices]))
        in_range_devices = path_model(potential_devices, (task.latitude, task.longitude), task.radius, cur_time, task.time, task.tolerance)
        mylogger.info("in_range_devices:")
        mylogger.info(str([str(d.id) for d in in_range_devices]))

        if len(in_range_devices) < task.num_devices and task.time - cur_time < 5 * 60 * 1000:
            mylogger.info("time is closing. going to find nearby devices")
            cur_devices = get_nearby_devices(task)
            in_range_devices.extend(cur_devices)

        if len(in_range_devices) < task.num_devices:
            mylogger.info('not enough in_range_devices ' + str(task.num_devices - len(in_range_devices)) + " more needed")

        candidates = filter_devices_by_battery_level(in_range_devices)
        mylogger.info("candidates for, " + str(task.id) + " are "+ str([str(d) for d in candidates]))

        def increment(device_obj):
                device_obj.tasksSatisfied += 1

        task.potential_devices = candidates
        list(map(increment, task.potential_devices))

    for task in task_list:
        scored_candidates = update_device_scores(task.potential_devices)
        mylogger.info("scored candidates for task" + str(task.id)  + " are " + str([str(d) for d in scored_candidates]))
        if len(scored_candidates) > 0:
            if not assign_task(task, scored_candidates, cur_time):
                un_finished_tasks.append(task)
        else:
            un_finished_tasks.append(task)
    return un_finished_tasks


def check_tasks_to_schedule(start_daemon=start_daemon):

    cur_time = current_milli_time()
    window_left = cur_time
    window_right = window_left + 20 * MINUTE
    mylogger.info('start checking tasks at ' + str(milliseconds_to_string(window_left)))
    mylogger.info('tasks interval to be included: ' + str(milliseconds_to_string(window_left)) +  ' and ' +  str(milliseconds_to_string(window_right)))
    task_list = list(map(Task, tasks.aggregate([
        {
            '$match': {'assigned': False}
        },
        {
            '$addFields': {
                'time2': {
                    '$add': [
                        '$time',
                        {'$multiply': ['$tolerance', 0.5]}
                    ]
                },
                'time3': {
                    '$subtract': [
                        '$time',
                        {'$multiply': ['$tolerance', 0.5]}
                    ]
                }
            }
        },
        {
            '$match': {
                'time2': {'$gte': window_left},
                'time3': {'$lt': window_right}
            }
        },
        {
            '$sort': {'time': 1}
        }
    ])))

    mylogger.info("task_list:" + str([str(t) for t in task_list]))

    if len(task_list) > 0:
        un_finished_tasks = schedule_tasks(task_list, cur_time)
        resumed = False
        for task in sorted(un_finished_tasks, key=lambda t: t.time):
            soonest = task.time - window_left - task.tolerance / 2
            latest = task.time - window_left + task.tolerance / 2 - 10 * SECOND
            # Note: latest cannot be the exact task.time + tolerance/2, because of the processing delay, when reschedule, the right bound will not be included.
            interval = max( MINUTE, soonest)

            if latest > interval:
                mylogger.info("recall check_task_to_schedule due to" + str(task.id) + ' after ' + str(interval/SECOND) + ' seconds. Now is ' + str(milliseconds_to_string(window_left)))
                start_daemon(interval / SECOND, check_tasks_to_schedule, [])
                resumed = True
                break
            else:

                mylogger.info("task " + str(task.id) +" is compromised")
                tasks.update_one({"_id": task.id}, {'$set': {"compromised": True, "num_devices": len(task.assignment_list)}})

        if not resumed:
            next_time = (window_right - window_left) / SECOND
            mylogger.info("tasks are scheduled, next calling is" + str(next_time) + ' seconds ' + ' Now is '+ str(milliseconds_to_string(window_left)))
            start_daemon(next_time, check_tasks_to_schedule, [])
    else:
        next_tasks = list(tasks.find({
            "finished": False,
            "assigned": False,
            "time": {"$gte": window_right}
        }).sort('time', 1).limit(1))

        mylogger.info('next_tasks: ' + str([str(t) for t in next_tasks]))

        if len(next_tasks) > 0:
            next_task = Task(next_tasks[0])
            gap = (next_task.time - next_task.tolerance / 2 - window_left)
            mylogger.info('start next check_tasks_to_schedule after' + str(gap/SECOND))
            start_daemon(gap / SECOND, check_tasks_to_schedule, [])
        else:
            mylogger.info('start next check_tasks_to_schedule after 20 minutes')
            start_daemon(20 * 60,  check_tasks_to_schedule, [])


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        mylogger.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        mylogger.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n", str(self.path), str(self.headers), post_data.decode('utf-8'))
        mylogger.info("TYPE: {}".format(type(post_data.decode('utf-8'))))
        data_json = json.loads(post_data.decode('utf-8'))
        mylogger.info("JSON data {}".format(data_json))
        if data_json["content"] == "newTaskInserted":
            mylogger.info("calling check_tasks_to_schedule")
            check_tasks_to_schedule()


def run(server_class=HTTPServer, handler_class=S, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    mylogger.info('Starting httpd...\n')
    check_tasks_to_schedule()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    mylogger.info('Stopping httpd...\n')


if __name__ == '__main__':
    run()
