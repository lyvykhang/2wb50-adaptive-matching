from random import choices

class Expert: # NOTE: definition includes extra expert and task type
    def __init__(self, id, a, delta):
        self.id = id
        self.a = a
        self.delta = delta

    def psi(self, z):
        if (self.id == 0):
            return z[0]*(1-(1-self.delta/2)) + z[1]*(1-self.a) + z[2]*(1-self.delta)
        elif (self.id == 1):
            return z[0]*(1-(1-self.delta/2)) + z[1]*(1-self.delta) + z[2]*(1-self.a)
        elif (self.id == 2): # extra expert
            return z[0]*(1-(1-self.a/2)) + z[1]*(1-self.delta) + z[2]*(1-self.delta)

    def phi(self, z):
        psi = self.psi(z)
        if (self.id == 0):
            return [(z[0]*(1-(1-self.delta/2)))/psi, (z[1]*(1-self.a))/psi, (z[2]*(1-self.delta))/psi]
        elif (self.id == 1):
            return [(z[0]*(1-(1-self.delta/2)))/psi, (z[1]*(1-self.delta))/psi, (z[2]*(1-self.a))/psi]
        elif (self.id == 2): # extra expert
            return [(z[0]*(1-(1-self.a/2)))/psi, (z[1]*(1-self.delta))/psi, (z[2]*(1-self.delta))/psi]
    
    def attempt(self, task):
        if (task.trueType == 0):
            if (self.id == 2):
                success = 1 - self.a/2
            else:
                success = 1 - self.delta/2
        elif (task.trueType == 1):
            if (self.id == 0):
                success = self.a
            elif (self.id == 1):
                success = self.delta 
            elif (self.id == 2):
                success = self.delta
        elif (task.trueType == 2): # extra task type
            if (self.id == 1):
                success = self.a
            else:
                success = self.delta

        return choices([0, 1], weights=[1-success, success])[0]
    
    def updateMixedType(self, task): # see equation (2) and section 3.1.
        task.mixedType = self.phi(task.mixedType)
