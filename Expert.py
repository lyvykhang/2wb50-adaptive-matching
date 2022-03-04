from random import choices

class Expert:
    def __init__(self, id, a, delta):
        self.id = id
        self.a = a
        self.delta = delta
    
    def attempt(self, task):
        if (task.trueType == 0): # task 1, same prob. of success for both
            success = 1 - self.delta/2
        elif (task.trueType == 1):
            if (self.id == 0):
                success = self.a
            elif (self.id == 1):
                success = self.delta 

        return choices([0, 1], weights=[1-success, success])[0]
    
    def updateMixedType(self, task): # see equation (2) and section 3.1.
        if (self.id == 0):
            psi = task.mixedType[0]*(1-(1-self.delta/2)) + task.mixedType[1]*(1-self.a)
            task.mixedType = [(task.mixedType[0]*(1-(1-self.delta/2)))/psi, (task.mixedType[1]*(1-self.a))/psi]
        elif (self.id == 1):
            psi = task.mixedType[0]*(1-(1-self.delta/2)) + task.mixedType[1]*(1-self.delta)
            task.mixedType = [(task.mixedType[0]*(1-(1-self.delta/2)))/psi, (task.mixedType[1]*(1-self.delta))/psi]