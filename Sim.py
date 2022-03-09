from random import choices, sample
import numpy as np
from Expert import Expert
from FES import FES
from Task import Task
from Event import Event
from SimResults import SimResults

class Sim:
    def __init__(self, a, delta, rate):
        self.a = a
        self.delta = delta
        self.rate = rate # lambda
    

### FUNCTIONS TO BE USED FOR BOTH ALGOS ###
    def sampleTaskType(self): # method for determining the type of a new task.
        return choices([0, 1])[0]
    

    def sampleExpert(self, experts): # randomly sample from a list and remove the sampled element (inplace).
        chosen = choices(experts)[0]
        experts.remove(chosen)
        return chosen


    def sampleInterArr(self): # interarrivals ~ Exp(Lambda).
        return np.random.exponential(1/self.rate) # the 1/... is intentional.
    

    def sampleServTime(self): # service time ~ Exp(1).
        return np.random.exponential(1)
    

### FUNCTIONS FOR BACKPRESSURE ALGO ###
    def checkTaskInSquare(self, z, i, j, eps): # (i, j) both in range [0, 1/eps-1].
        z1, z2 = int(round(z[0]/eps, 12)), int(round(z[1]/eps, 12)) # take the integer component of z/eps (rounded to 12 d.p. to reduce misclassification...
        # ... due to rounding errors), if this is equal to (i, j), the mixed-type is in the square. 
        return z1 == i and z2 == j


    def countTasksInSquare(self, pool, i, j, eps): # go through the pool of tasks at time t, count any task with mixed type in set A_{i, j}.
        N_ij = 0
        for task in pool:
            if self.checkTaskInSquare(task.mixedType, i, j, eps):
                N_ij += 1
        return N_ij
            

    def computeBackpressure(self, pool, expert, z, eps): # for a specific (expert, task.mixedType) pairing.
        i1, j1 = int(round(z[0]/eps, 12)), int(round(z[1]/eps, 12)) # see checkTaskInSquare.
        i2, j2 = int(round(expert.phi(z)[0]/eps, 12)), int(round(expert.phi(z)[1]/eps, 12))
        
        N_i1j1 = self.countTasksInSquare(pool, i1, j1, eps)
        N_i2j2 = self.countTasksInSquare(pool, i2, j2, eps)
        return N_i1j1 - expert.psi(z)*N_i2j2
                

### MAIN SIM FUNCTION ###   
    def sim(self, T, eps=None): # NOTE: runs Random algo if eps argument is not supplied.
        idleExperts = [Expert(i, self.a, self.delta) for i in range(0, 2)]
        fes = FES()
        t = 0
        pool = []
        results = SimResults()

        arrTime = t + self.sampleInterArr() # schedule first arrival event.
        firstTask = Task(self.sampleTaskType(), arrTime)
        fes.add(Event(Event.ARRIVAL, arrTime, firstTask)) 
        
        while(t < T):
            e = fes.next()
            task = e.task
            t = e.arrTime

            if (e.type == Event.ARRIVAL):
                if (len(idleExperts) == 0): # no free experts -> task goes directly to pool. 
                    pool.append(task)
                else: # process task directly if there are free experts.
                    ex = self.sampleExpert(idleExperts) # assign random idle expert. NOTE: sampleExpert removes expert from idleExperts.
                    attemptResult = ex.attempt(task) # perform task and check outcome.
                    servTime = self.sampleServTime()
                    
                    if (attemptResult == 0): # if failed, update mixed type and move task to pool. 
                        ex.updateMixedType(task)
                        pool.append(task)
                    else:
                        results.registerSojournTime(t + servTime, task)

                    # need to add a "departure" event regardless of success/fail...
                    fes.add(Event(Event.DEPARTURE, t + servTime, task, ex))  #... so the pool of outstanding tasks can be interacted with. 
                    
                arrTime = t + self.sampleInterArr() # schedule next event.
                newTask = Task(self.sampleTaskType(), arrTime)
                fes.add(Event(Event.ARRIVAL, arrTime, newTask))
            
            elif (e.type == Event.DEPARTURE):
                ex = e.expert
                if (len(pool) == 0): # if no outstanding tasks in the pool, expert becomes idle again.
                    idleExperts.append(ex)
                else:
                    if (eps is not None): # Backpressure algorithm.
                        backpressures = [self.computeBackpressure(pool, ex, t.mixedType, eps) for t in pool] # compute bp for each task.
                        maxes = [idx for (idx, i) in enumerate(backpressures) if i == max(backpressures)] # idx of task(s) with max bp. 
                        newTask = pool[sample(maxes, 1)[0]] # randomly choose one of the max bp tasks.
                    elif (eps is None): # Random algorithm.
                        newTask = sample(pool, 1)[0] # NOTE: does NOT yet remove task from the pool.

                    attemptResult = ex.attempt(newTask)
                    servTime = self.sampleServTime()
                    
                    if (attemptResult == 0):
                        ex.updateMixedType(newTask)
                    else: # if success, remove from pool.
                        pool.remove(newTask)
                        results.registerSojournTime(t + servTime, newTask)

                    fes.add(Event(Event.DEPARTURE, t + servTime, newTask, ex))

        results.updateMeanSojournTime()
        return results
