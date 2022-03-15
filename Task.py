class Task:
    def __init__(self, trueType, arrTime, extra=None):
        self.trueType = trueType
        if extra is None:
            self.mixedType = [1/2, 1/2, 0]
        else: # 3 different task types
            self.mixedType = [1/3, 1/3, 1/3]
        self.arrTime = arrTime