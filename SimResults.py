class SimResults:
    def __init__(self):
        self.sojournTimes = []
        self.meanSojournTime = 0
    
    def registerSojournTime(self, t, task):
        self.sojournTimes.append(t - task.arrTime)
    
    def updateMeanSojournTime(self):
        self.meanSojournTime = sum(self.sojournTimes)/len(self.sojournTimes)