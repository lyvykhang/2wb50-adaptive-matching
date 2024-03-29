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
    def sampleTaskType(self, extra=None): # method for determining the type of a new task.
        if extra is None: # just 2 task types
            return choices([0, 1])[0]
        return choices([0, 1, 2])[0] # 3 task types
    

    def sampleExpert(self, experts): # randomly sample from a list and remove the sampled element (inplace).
        chosen = choices(experts)[0]
        experts.remove(chosen)
        return chosen


    def sampleInterArr(self): # interarrivals ~ Exp(Lambda).
        return np.random.exponential(1/self.rate) # the 1/... is intentional.
    

    def sampleServTime(self): # service time ~ Exp(1).
        return np.random.exponential(1)
    

### FUNCTIONS FOR BACKPRESSURE ALGO ###
    # k is the 3rd dimension for the mixed type when using the extra feature.
    def checkTaskInSquare(self, z, i, j, k, eps): # (i, j) both in range [0, 1/eps-1].
        # take the integer component of z/eps (rounded to 12 d.p. to reduce misclassification...
        # ... due to rounding errors), if this is equal to (i, j), the mixed-type is in the square. 
        z1, z2, z3 = int(round(z[0]/eps, 12)), \
                int(round(z[1]/eps, 12)), \
                int(round(z[2]/eps, 12)) 

        return (z1 == i and z2 == j and z3 == k)


    def countTasksInSquare(self, pool, i, j, k, eps): # go through the pool of tasks at time t, count any task with mixed type in set A_{i, j}.
        N_ijk = 0
        for task in pool:
            if self.checkTaskInSquare(task.mixedType, i, j, k, eps):
                N_ijk += 1
        return N_ijk
            

    def computeBackpressure(self, pool, expert, z, eps): # for a specific (expert, task.mixedType) pairing.
        # if the extra feature is not requested, the 3rd dimension will be 0
        i1, j1, k1 = int(round(z[0]/eps, 12)), int(round(z[1]/eps, 12)), int(round(z[2]/eps, 12)) # see checkTaskInSquare.
        i2, j2, k2 = int(round(expert.phi(z)[0]/eps, 12)), int(round(expert.phi(z)[1]/eps, 12)), int(round(expert.phi(z)[2]/eps, 12))

        N_i1j1k1 = self.countTasksInSquare(pool, i1, j1, k1, eps)
        N_i2j2k2 = self.countTasksInSquare(pool, i2, j2, k2, eps)

        return N_i1j1k1 - expert.psi(z)*N_i2j2k2
                

### MAIN SIM FUNCTION ###   
    # NOTE: runs Random algo if eps argument is not supplied.
    # NOTE: the extra feature won't run if extra argument is not supplied
    def sim(self, T, eps=None, extra=None): 
        noExperts = 2
        if extra is not None:
           noExperts = 3 
        idleExperts = [Expert(i, self.a, self.delta) for i in range(0, noExperts)]
        fes = FES()
        t = 0
        pool = []
        results = SimResults()

        arrTime = t + self.sampleInterArr() # schedule first arrival event.
        firstTask = Task(self.sampleTaskType(extra), arrTime, extra)
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
                newTask = Task(self.sampleTaskType(extra), arrTime, extra)
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
