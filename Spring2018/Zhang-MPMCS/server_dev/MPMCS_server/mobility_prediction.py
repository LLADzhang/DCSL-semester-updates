from pymongo import MongoClient
from  math import sqrt
from geopy.distance import vincenty
from datetime import datetime
from itertools import groupby
from Utils import locations, MINUTE, mylogger, range_query
from Device import Device

def lerp(a, b, f):
    return a * (1 - f) + b * f


# Calculate the distance between two points
def distance_sq(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


# Rounds each element of a vector to the nth decimal place
def roundv(v, n):
    return [round(x, n) for x in v]


# Get the last element in an iterable
def last(iterable, default=None):
    last = next(iterable, default)
    for last in iterable:
        pass
    return last


# Binary search
def binary_search(a, x, lo=0, hi=None, key=lambda x: x):
    hi = hi if hi is not None else len(a)

    while lo < hi:
        mid = (lo + hi) // 2
        v = key(a[mid])
        if v < x:
            lo = mid + 1
        elif v > x:
            hi = mid
        else:
            return mid

    return -1


# Compares two trajectories normalizing the points such that the time between each is dt
def compare_trajectory(t1, t2, dt):
    def nextPoint(a, i, t):
        # a: the list of dictionary, each dic is {"latitude": float, "longitude": float, "timeStamp": int}
        # i: current index of a. starts from 0
        # t: the target time

        while a[i]["timeStamp"] - t < dt:
            i += 1
            if i >= len(a):
                return None, None

        curr, prev = a[i], a[i - 1]
        f = (t + dt - prev["timeStamp"]) / (curr["timeStamp"] - prev["timeStamp"])

        return {
                   "location": [
                       lerp(prev["location"][0], curr["location"][0], f),
                       lerp(prev["location"][1], curr["location"][1], f)
                   ],
                   "timeStamp": lerp(prev["timeStamp"], curr["timeStamp"], f)
               }, i

    error = 0
    i, j = 0, 0
    a, b = t1[i], t2[j]

    while a is not None and b is not None:
        error += sqrt(distance_sq(a["location"], b["location"]))
        a, i = nextPoint(t1, i, a["timeStamp"])
        b, j = nextPoint(t2, j, b["timeStamp"])

    return error


def path_model(device_list, location, radius, cur_time, target_time, tolerance):
    # device_list: list of Device objects
    # location: [latitude: float, longitude: float]
    # radius: location tolerance (meters)
    # cur_time: current time (milliseconds)
    # target_time: epoch time (milliseconds) at which the task should occur
    # tolerance: time tolerance in milliseconds

    table = locations
    # Digits of significance for latitude/longitude values
    degree_digits = 3
    # The predicted trajectory starts at the current time and ends at the target time
    trajectory_length = target_time - cur_time
    # The current trajectory ends where the predicted trajectory starts and is the same length
    cur_trajectory_start = cur_time - trajectory_length
    # When comparing the current trajectory to the predicted trajectory, these are the steps
    # (in milliseconds) that they are normalized to
    steps = trajectory_length / (5 * 60 * 1000)

    tolerable_radius = 100

    for device in device_list:
        mylogger.info('\n\n\n\n\npredicting for device ' + str(device.id))

        # Get the current trajectory so it can be compared against the predicted trajectories
        cur_trajectory = list(table.find({
            "uid": device.id,
            "timeStamp": {
                "$gte": cur_trajectory_start,
                "$lt": cur_time
            },
            "location": {
                "$ne": [0, 0]
            }
        }).sort("timeStamp", 1))

        mylogger.info('cur_trajectory length=' +str(len(cur_trajectory)))

        if len(cur_trajectory) == 0:
            device.probability = None
            continue

        #  Find points near to the first point of the current trajectory
        cur_tra_first_point = cur_trajectory[0]["location"]
        #near_points = table.find({
        #    "uid": device.id,
        #    "timeStamp": {
        #        "$lt": cur_time - trajectory_length
        #    }
        #}).sort("timeStamp", 1)
        #near_points = [x for x in near_points if vincenty(x['location'], cur_tra_first_point).meters <= tolerable_radius]

        near_points = range_query(table, cur_tra_first_point[::-1], tolerable_radius, 0, cur_time-trajectory_length,
                              {'location': 1, 'timeStamp': 1}).sort('timeStamp', 1)
        # Starting times of the predicted trajectories
        start_times = [
            last(g)["timeStamp"] for k, g in
            groupby(near_points, lambda x: roundv(x["location"], degree_digits))
        ]

        # TODO: If there are many start_times then many adjust probability to reflect uncertainty

        mylogger.info('start_times length=' + str(len(start_times)))

        if len(start_times) == 0:
            device.probability = None
            continue

        # All the predicted trajectories will be contained in this list
        historical_trajectory = list(table.find({
            "uid": device.id,
            "timeStamp": {
                "$gte": start_times[0],
                "$lt": start_times[-1] + trajectory_length
            }
        }))

        mylogger.info('start_times first/last= ' + str(start_times[0]) + " " + str((start_times[-1])))
        mylogger.info('historical_trajectory length=' + str(len(historical_trajectory)))

        def compare_trajectory_starting_at(x):
            i = binary_search(historical_trajectory, x, key=lambda x: x["timeStamp"])
            tra = historical_trajectory[i:]
            c = compare_trajectory(tra, cur_trajectory, 5 * 60 * 1000)
            # mylogger.info('compare_trajectory', c)
            return tra, c

        best_tra, best_error = min(
            (compare_trajectory_starting_at(x) for x in start_times),
            key=lambda x: x[1]
        )

        predicted_location = best_tra[-1]["location"]

        mylogger.info('best_error' + str(best_error))
        mylogger.info('predicted location' + str(predicted_location))
        mylogger.info('distance from target location'+  str(vincenty(predicted_location, location).meters))

        device.probability = int(vincenty(best_tra[-1]["location"], location).meters < radius) \
            if best_error < steps * tolerable_radius else None

    return list(filter(lambda d: d.probability is not None and d.probability > 0, device_list))


