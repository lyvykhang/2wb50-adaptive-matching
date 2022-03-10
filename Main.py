from Expert import Expert
from FES import FES
from Task import Task
from Event import Event
from SimResults import SimResults
from Sim import Sim

import numpy as np
from scipy.stats import t

sim = Sim(0.5, 0.1, 0.85)
results = sim.sim(100000, 1/40)
print(len(results.sojournTimes))
print(results.meanSojournTime)
print(results.sojournTimes)

print("Get 95% confidence interval")
confidence = 0.95
m = results.meanSojournTime # mean
s = np.array(results.sojournTimes).std() # standard deviation
dof = len(results.sojournTimes)-1 # degrees of freedom
t_crit = np.abs(t.ppf((1-confidence)/2, dof)) # calculate t_crit using inverse cdf 
print((m-s*t_crit/np.sqrt(len(results.sojournTimes)), m+s*t_crit/np.sqrt(len(results.sojournTimes))))