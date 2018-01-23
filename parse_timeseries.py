import pdb

class timeseries():
    def __init__(self,data):
        # Give data to timeseries object
        self.data = data
        
    
    def describe(self):

        # Determine if monotonic
        monotonic, increase, decrease = self.is_monotonic()
    
        # Determine if past or future
        past, future = self.past_or_future()
    
        # Elaborate description
        if not (past and future) and monotonic:
            description = "will "*future + "increase"*increase + "decrease"*decrease + "d"*past + " steadily from " +  self.data[0].height() + " to " + self.data[-1].height() + " " + self.data[0].units()
        elif (past and future) and monotonic:
            description = "started at " + data[0].height() + " " + self.data[-1].units() + " and will continue to " + "increase"*increase + "decrease"*decrease + " steadily to " + self.data[-1].height() + " " + self.data[-1].units()
        elif not (past and future):
            # Come back to this to better descibe timeseries
            description = "will be "*future + "was "*past + "between " + str(min([float(d.height()) for d in self.data])) + " and " + str(max([float(d.height()) for d in self.data])) + " " + self.data[0].units()
        else:
            raise ValueError("No description of combinded timeseries")
    
        return description
        

    def is_monotonic(self):
        heights = [float(d.height()) for d in self.data]
    
        diffs = list()
        for h0,h1 in zip(heights[:-1],heights[1:]):
            diffs.append(h1-h0)

        # Determine if timeseries monotonic
        if all([d>=0 for d in diffs]):
            increase, decrease = True, False
        elif all([d<=0 for d in diffs]):
            increase, decrease = False, True
        else:
            increase, decrease = True, True
    
        monotonic = not (increase and decrease)
    
        return monotonic, increase, decrease

    def past_or_future(self):
        # Determine if looking at past of future data
        if all([d.key()=='observed' for d in self.data]):
            past, future = True, False
        elif all([d.key()=='forecast' for d in self.data]):
            past, future = False, True
        else:
            past, future = True, True
        
        return past, future