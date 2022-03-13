from Expert import Expert
from FES import FES
from Task import Task
from Event import Event
from SimResults import SimResults
from Sim import Sim

import numpy as np
from scipy.stats import t

import pandas as pd

def getConfidenceInterval(results):
    confidence = 0.95
    m = results.meanSojournTime # mean
    s = np.array(results.sojournTimes).std() # standard deviation
    dof = len(results.sojournTimes)-1 # degrees of freedom
    t_crit = np.abs(t.ppf((1-confidence)/2, dof)) # calculate t_crit using inverse cdf 
    return (round((m-s*t_crit/np.sqrt(len(results.sojournTimes))), 2), round((m+s*t_crit/np.sqrt(len(results.sojournTimes))), 2))
    
def dfToLatex(df, caption):
    df.columns = [0.1, 0.2, 0.3, 0.4, 0.5]
    df.index = [0.75, 0.77, 0.79, 0.81, 0.83, 0.85]
    print("\\begin{table}[h!]")
    print("\\resizebox{\textwidth}{!}{")
    print(df.to_latex())
    print("}")
    print(f"\\caption{{{caption}}}")
    print("\\end{table}")

def getTable(a, eps, caption):
    df = pd.DataFrame(data = None, index = range(6), columns = range(5))
    a = a
    rate = 0.75
    for i in range(6):
        rate = rate + (i * 0.2)
        delta = 0.1
        for j in range(5):
            delta = rate + (j * 0.1)
            sim = Sim(a, delta, rate)
            results = sim.sim(10000, eps)
            mean = round(results.meanSojournTime, 2)
            ci = getConfidenceInterval(results)
            df.loc[i, j] = '{0} {1}'.format(str(mean), str(ci))
    dfToLatex(df, caption)

print("Do one test run")
sim = Sim(0.5, 0.1, 0.85)
results = sim.sim(10000, 1/40)
print(len(results.sojournTimes))
print(results.meanSojournTime)
print(results.sojournTimes)

print("Get 95% confidence interval")
print(getConfidenceInterval(results))

print("Output LaTeX table for a=1/2 and random algorithm")
getTable(0.5, None, "a=1/2 and random algorithm")

print("Output LaTeX table for a=1/2 and backpressue 1/40")
getTable(0.5, (1/40), "a=1/2 and backpressure 1/40")