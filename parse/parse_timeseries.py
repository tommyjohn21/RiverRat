import pdb
import numpy as np
from scipy import interpolate
import parse

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
        self.crests, self.cidx, self.troughs, self.tidx = self.convert_tides()
        
        # Code to gut-check spline fit
        # if True: self.plot()
        
        # Compute range object
        self.range = range(self.heights)
        
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
    
    def find_data_by_dates(self,req):

        # Output req in self object
        self.req = req
        
        # Find xml data that that matches dates in req
        i_bool = [x.time().date() in [y.date() for y in req.dates] for x in self.data]
        
        # Raise error if no matching data
        if not any(i_bool): return
        
        # Adjust heights, times, etc
        [setattr(self,fki,[getattr(self,fki)[i] for i,b in enumerate(i_bool) if b]) for fki in ["heights","times"]]
        
        # Reset range once heights have been modified
        self.range = range(self.heights)
        
        # Still need to deal with spline
        self.spline.t = np.arange(self.times[0]-60,self.times[-1]+60,5)
        
        # Adjust crests and troughs (keep if in the restriced time)
        [setattr(self.spline,fki,[x for x in getattr(self.spline,fki) if x >= self.spline.t[0] and x <= self.spline.t[-1]]) for fki in ["crests","troughs"]]
        
        # Restrict data by bool value
        self.data = [self.data[i] for i,b in enumerate(i_bool) if b]
        
        # Convert tides from (modified) spline timestamps into xml data points
        self.crests, self.cidx, self.troughs, self.tidx = self.convert_tides()
        
        # Protocol for ploting sliced (date-restricted) data
        # if False: self.plot()
        
        return self
    
    def plot(self):
        try:
            import matplotlib.pyplot as plt

            plt.plot(self.spline.t,self.spline.s(self.spline.t))
            plt.hold(True)
            [plt.plot(self.times[i],self.heights[i],'ro',markersize=10) for i in self.cidx]
            [plt.plot(self.times[i],self.heights[i],'ro',markersize=10) for i in self.tidx]
            [plt.plot(i,self.spline.s(i),'g.',markersize=15) for i in self.spline.crests]
            [plt.plot(i,self.spline.s(i),'g.',markersize=15) for i in self.spline.troughs]
            plt.plot(self.times,self.heights,'kx')
            plt.show()
            pdb.set_trace()
        except:
            pass
        
    def describe(self):

        # Create description
        return parse.description(self)

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
        # (default spline smootheness is a heuristic at best)
        self.s = interpolate.UnivariateSpline(data.times,data.heights,k=4,s=0.5)

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
            if d_1.__call__(i,1) < -1e-8:
                crests.append(i)

        # Define troughs
        troughs = list()
        for i in points:
            if d_1.__call__(i,1) > 1e-8:
                troughs.append(i)

        return crests, troughs