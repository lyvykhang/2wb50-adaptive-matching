class Event:
    ARRIVAL = 0
    DEPARTURE = 1

    def __init__(self, typ, arrTime, task, expert=None):
        self.type = typ
        self.arrTime = arrTime
        self.task = task
        self.expert = expert # NOTE: optional param, only defined if event type is DEPARTURE.
    
    def __lt__(self, other):
        return self.arrTime < other.arrTime