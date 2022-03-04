from random import choices, sample
import numpy as np
import Expert
import FES
import Task
import Event
import SimResults

class SimRandom:
    def __init__(self, a, delta, rate):
        self.a = a
        self.delta = delta
        self.rate = rate # lambda
    
    def sampleTaskType(self): # method for determining the type of a new task.
        return choices([0, 1])[0]
    
    def sampleExpert(self, experts): # randomly sample from a list and remove the sampled element (inplace).
        chosen = choices(experts)[0]
        experts.remove(chosen)
        return chosen

    def sampleInterArr(self): # interarrival distribution Exp(Lambda).
        return np.random.exponential(1/self.rate) # the 1/... is intentional.
    
    def sampleServTime(self): # service time distribution Exp(1).
        return np.random.exponential(1)
    
    def sim(self, T):
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
                    ex = self.sampleExpert(idleExperts) # assign random idle expert.
                    attemptResult = ex.attempt(task) # perform task and check outcome.

                    if (attemptResult == 0): # if failed, update mixed type and move task to pool. 
                        ex.updateMixedType(task)
                        # print(task.mixedType)
                        # print(task.trueType)
                        pool.append(task)
                    else:
                        results.registerSojournTime(t, task)

                    servTime = self.sampleServTime() # need to add a "departure" event regardless of success/fail...
                    fes.add(Event(Event.DEPARTURE, t + servTime, task, ex))  #... so the pool of outstanding tasks can be interacted with. 
                    
                arrTime = t + self.sampleInterArr() # schedule next event.
                newTask = Task(self.sampleTaskType(), arrTime)
                fes.add(Event(Event.ARRIVAL, arrTime, newTask))
            
            elif (e.type == Event.DEPARTURE):
                ex = e.expert
                if (len(pool) == 0): # if no outstanding tasks in the pool, expert becomes idle again.
                    idleExperts.append(ex)
                else:
                    newTask = sample(pool, 1)[0] # assign random task from pool. NOTE: does not yet remove task from the pool.
                    attemptResult = ex.attempt(newTask)
                    
                    if (attemptResult == 0):
                        ex.updateMixedType(newTask)
                        # print(task.mixedType)
                        # print(task.trueType)
                    else: # if success, remove from pool.
                        pool.remove(newTask)
                        results.registerSojournTime(t, newTask)

                    servTime = self.sampleServTime()
                    fes.add(Event(Event.DEPARTURE, t + servTime, newTask, ex))
        # print(pool)
        # print(fes.events)
        # print(t)        
        results.updateMeanSojournTime()
        return results