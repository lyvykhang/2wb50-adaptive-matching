from Expert import Expert
from FES import FES
from Task import Task
from Event import Event
from SimResults import SimResults
from Sim import Sim

sim = Sim(0.5, 0.1, 0.85)
results = sim.sim(100, 1/40)
print(len(results.sojournTimes))
print(results.meanSojournTime)
print(results.sojournTimes)


