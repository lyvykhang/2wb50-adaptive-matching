from turtle import title
from Expert import Expert
from FES import FES
from Task import Task
from Event import Event
from SimResults import SimResults
from Sim import Sim

import numpy as np
from scipy.stats import t
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

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

def dfToPlot(df):
    plt.plot(df)
    plt.legend([0.1, 0.2, 0.3, 0.4, 0.5], title="delta")
    plt.ylabel("Mean sojourn time")
    plt.xlabel("Rate / Lamba")
    plt.xticks(df.index, df.index)
    date = datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig("results_{0}.png".format(date))
    plt.clf()

def getTable(a, caption, eps=None, extra=None):
    df = pd.DataFrame(data = None, index = range(6), columns = range(5))
    dfForPlot = pd.DataFrame(data = None, index = range(6), columns = range(5))
    for i in range(6):
        rate = 0.75 + (i * 0.02)
        for j in range(5):
            delta = 0.1 + (j * 0.1)
            sim = Sim(a, delta, rate)
            results = sim.sim(10000, eps=eps, extra=extra)
            mean = round(results.meanSojournTime, 2)
            ci = getConfidenceInterval(results)
            df.loc[i, j] = '{0} {1}'.format(str(mean), str(ci))
            dfForPlot.loc[i, j] = mean
    dfToLatex(df, caption)
    dfToPlot(dfForPlot)

print("Do one test run")
sim = Sim(0.5, 0.1, 0.79)
results = sim.sim(10000, eps=1/40, extra=1)
print(len(results.sojournTimes))
print(results.meanSojournTime)
print(results.sojournTimes)

print("Get 95% confidence interval")
print(getConfidenceInterval(results))

print("Output LaTeX table for a=1/2 and random algorithm")
getTable(0.5, "a=1/2 and random algorithm")

print("Output LaTeX table for a=1/2 and backpressue 1/40")
getTable(0.5, "a=1/2 and backpressure 1/40", eps = (1/40))

print("Output LaTeX table with extra features for a=1/2 and backpressue 1/40")
getTable(0.5, "a=1/2 and backpressure 1/40, with extra features", eps = (1/40), extra=1)
