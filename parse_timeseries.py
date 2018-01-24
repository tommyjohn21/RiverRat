import pdb
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

class timeseries():
    def __init__(self,data):
        # Give data to timeseries object
        self.data = data
        
        # Extract height values
        self.heights = map(lambda x: float(x.height()), self.data)
        
        # Extract time values: convert to minutes, normalize to first time-point
        self.times = map(lambda x: x.time().timestamp/float(60),self.data)
        self.times = [x - self.times[0] for x in self.times]
        
        # Create (smooth) spline interpolation
        self.spline = spline(self)
        
        # Convert tides from spline timestamps into xml data points
        self.crests, cidx, self.troughs, tidx = self.convert_tides()
        
        # Code to gut-check spline fit
        if False:
            plt.plot(self.times,self.heights,'*')
            plt.hold(True)
            plt.plot(self.spline.t,self.spline.s(self.spline.t))
            [plt.plot(self.times[i],self.heights[i],'x') for i in cidx]
            [plt.plot(self.times[i],self.heights[i],'x') for i in tidx]
            plt.show()
            pdb.set_trace()
        
        pdb.set_trace()
        
        # Compute range object
        self.range = range(self.heights)

    
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
        
    def convert_tides(self):
        # Convert time points in spline.crests, etc. to datum in self
        crests, cidx, troughs, tidx = ([] for i in [0,1,2,3]) # initialize lists
        for tidekey in ["crests","troughs"]:
            tidepoint = getattr(self.spline,tidekey)
            for t in tidepoint:
                # Create boolean array that assumes that the actual crest/trough is +/- 18 hrs of the spline crest/trough
                t_bool = np.abs([time - t for time in self.times]) < 18*60
                # Get index of true bools
                tidex = [i for i,b in enumerate(t_bool) if b]
                # Compare self.heights[tidx] to find the actual extremum
                if tidekey == "crests":
                    cidx.append(tidex[np.argmax([self.heights[i] for i in tidex])])
                    crests.append(self.data[cidx[-1]])
                elif tidekey == "troughs":
                    tidx.append(tidex[np.argmin([self.heights[i] for i in tidex])])
                    troughs.append(self.data[tidx[-1]])

        return crests, cidx, troughs, tidx


class range:
    
    def __init__(self,values):

        # Things of interest
        self.max = str(max(values))
        self.min = str(min(values))
        self.range = str(max(values) - min(values))
        
    def humanize(self):
        
        # Human readable range string
        return "between {} and {} feet".format(self.min,self.max)
        
class spline:
    
    def __init__(self,data):
        # Do intepolation with scipy interpolate
        # (use default spline of 0.05--this is a heuristic at best)
        self.s = interpolate.UnivariateSpline(data.times,data.heights,k=4,s=0.05)
        
        # Define times, mostly for plotting purposes
        self.t = np.arange(data.times[0],data.times[-1],5)
        
        # Define crests and troughs
        self.crests, self.troughs = self.tides(data)
        
    def tides(self,data):
        d_1 = self.s.derivative(1)
        points = d_1.roots()
        
        # Define crests
        crests = list()
        for i in points:
            if d_1.__call__(i,1) < 0:
                crests.append(i)

        # Define crests
        troughs = list()
        for i in points:
            if d_1.__call__(i,1) > 0:
                troughs.append(i)
        
        return crests, troughs        