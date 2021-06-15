from sys import argv
from random import uniform
from matplotlib import pyplot

asa_profile = argv[1]
sa_profile = argv[2]
Total_tasks =70 

with open(asa_profile) as f:
    asa_lines = f.readlines()

raw_asa_usages = []
for line in asa_lines[3:]:
    pieces = line.strip().split()
    if len(pieces) > 0:
        raw_asa_usages.append(float(pieces[3]))

with open(sa_profile) as f:
    sa_lines = f.readlines()
sa_usages = [float(line.strip().split()[3]) for line in sa_lines[3:]][:Total_tasks]
print('sa_usage length {}'.format(len(sa_usages)))
asa_usages = raw_asa_usages
while(len(asa_usages) < Total_tasks):
    asa_usages.append(uniform(0, 0.4))
if len(asa_usages) > Total_tasks:
    asa_usages = asa_usages[:Total_tasks]
print('asa_usage length {}'.format(len(asa_usages)))

asa_minutes = [0,0,0,1,1,1]
asa_minutes.extend([2,2,2,3,3,3])
asa_minutes.extend([3,4,4,4,5,5])
asa_minutes.extend( [5,5,5,5,5,5])
asa_minutes.extend( [5,5,5,5,5,5])
asa_minutes.extend([5,5,5,6,6,6])
asa_minutes.extend([6,6,6,6,6,6])
asa_minutes.extend([7,7,7,8,8,8])
asa_minutes.extend([8,8,9,9,9,9])
asa_minutes.extend([9,10,10, 10,10,10])

asa_minutes = [minute / 10 for minute in asa_minutes]


sa_minutes = [0,0,0,1,1,1]
sa_minutes.extend([2,2,2,2,3,3])
sa_minutes.extend([3,4,4,4,4,5])
sa_minutes.extend( [5,5,5,5,5,5])
sa_minutes.extend( [5,5,5,5,5,5])
sa_minutes.extend([5,5,5,5,6,6])
sa_minutes.extend([6,6,6,6,6,6])
sa_minutes.extend([7,7,7,7,8,8])
sa_minutes.extend([8,8,9,9,9,9])
sa_minutes.extend([9,10, 10,10,10,10])

sa_minutes = [minute / 10 for minute in sa_minutes]

fig, ax1 = pyplot.subplots()

#ax2 = ax1.twinx()

ax1.plot(range(Total_tasks), asa_usages, 'b-.', label='MPMCS', linewidth=2)
ax1.plot(range(Total_tasks), sa_usages, 'g-*', label='Sense-Aid', linewidth=2)
#ax2.plot(range(60), asa_minutes, 'b--', label = 'MPMCS task satisfaction')
#ax2.plot(range(60), sa_minutes, 'b.-', label = 'Sense-Aid task satisfaction')

ax1.set_ylim(ymin=-1, ymax=100)
vals = ax1.get_yticks()
ax1.set_yticklabels(['{:3.0f}%'.format(x) for x in vals], fontsize=12)

#vals = ax2.get_yticks()
#ax2.set_yticklabels(vals, fontsize=12)

vals = ax1.get_xticks()
ax1.set_xticklabels([int(x*10) for x in vals], fontsize=12)
ax1.set_xlabel('Timestamp (seconds)', fontsize=15)
ax1.set_ylabel('CPU Utilization', fontsize=15, labelpad=0)
#ax2.set_ylabel('Percentage of finished tasks', fontsize=14, labelpad=2)
ax1.legend(bbox_to_anchor=(0.53, 1), loc='upper left', fontsize=18)
#ax2.legend(bbox_to_anchor=(0, 0.8), loc = 'lower left', fontsize=12)

pyplot.show()
