import matplotlib.pyplot as plt
import numpy as np
senseaid_gini = [0.49, 0.52, 0.42]
asa_gini = np.array([0.37 for i in range(3)])

plt.plot(range(len(senseaid_gini)), senseaid_gini, 'b*', label="senseaid")
plt.plot(range(len(asa_gini)), asa_gini, 'k', label='asa')
plt.ylabel("Gini coefficient")
plt.xticks(range(len(senseaid_gini)), ('60 secs', '30 secs',  '15 secs'))
plt.title("Scheduling equality comparison")
plt.legend()
plt.show()

