import matplotlib.pyplot as plt
from json import load
import numpy as np
from sys import argv

def gini(x):
    # (Warning: This is a concise implementation, but it is O(n**2)
    # in time and memory, where n = len(x).  *Don't* pass in huge
    # samples!)

    # Mean absolute difference
    mad = np.abs(np.subtract.outer(x, x)).mean()
    # Relative mean absolute difference
    rmad = mad/np.mean(x)
    # Gini coefficient
    g = 0.5 * rmad
    return g

if len(argv) != 3:
    print("Usage: asa_result_json sense_aid_result_json")
    exit(0)

asa_result = load(open(argv[1]))

senseaid_result = load(open(argv[2]))

asa_users = {}
for task in asa_result:
    for user in task['assignment_list']:
        if user in asa_users:
            asa_users[user] += 1
        else:
            asa_users[user] = 1
senseaid_users={}
for task in senseaid_result:
    for user in task['assignment_list']:
        if user in senseaid_users:
            senseaid_users[user] += 1
        else:
            senseaid_users[user] = 1


print(senseaid_users)
print("Gini coefficient for Sense-Aid: " + str(gini(np.array(list(senseaid_users.values())))))

print(asa_users)
print("Gini coefficient for ASA: " + str(gini(np.array(list(asa_users.values())))))


