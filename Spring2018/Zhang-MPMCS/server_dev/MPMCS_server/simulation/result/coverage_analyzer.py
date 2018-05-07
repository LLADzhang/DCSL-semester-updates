import matplotlib.pyplot as plt
from json import load
from sys import argv

if len(argv) != 4:
    print("usage: asa_result_json_file senseaid_result_json_file, seconds in sense-aid")
    exit(0)

asa_result = load(open(argv[1]))
tasks = []
asa_satisfication = []
for task in asa_result:
    tasks.append(task['_id'])
    if len(task['assignment_list']) >= task['num_devices']:
        asa_satisfication.append(1)
    else:
        asa_satisfication.append(0)
print(len(tasks))
print(len(asa_satisfication))

sense_aid_result = load(open(argv[2]))
sense_aid_satisfication = []
for task in sense_aid_result:
    if task['assigned']:
        sense_aid_satisfication.append(1)
    else:
        sense_aid_satisfication.append(0)
print(sense_aid_satisfication)

plt.plot(tasks, asa_satisfication, 'xg', label="ASA task satisfaction")
plt.plot(tasks, sense_aid_satisfication, '+r', label="Sense-Aid task satisfaction")
plt.xlabel("Task index")
plt.ylabel("Satisfied or not")
plt.title("Task satisfaction with "+ argv[3] + " seconds polling")
plt.legend()
plt.show()
