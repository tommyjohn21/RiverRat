import parse_request
import arrow
import cfg
from parse_xml import timeline
from parse_timeseries import timeseries
import pdb

class look_up_heights:
    def __init__(self,dateslot):
    
        # Parse request
        self.req = parse_request.date_request(dateslot)
        
        # Find date matches
        self.matches = timeline().find_data_by_dates(self.req)
        
        # Grab date string
        self.datestr = date_parser(self.req)
        
        if len(self.matches) == 0:
            self.speech_output = "River data is not available for this time period"
            return
        else:
            try:
                self.speech_output = self.datestr + ", the river " + timeseries(self.matches).describe()
            except:
                self.speech_output = "River data cannot be described for this time period"

class current_height:
    def __init__(self):
        
        # Grab last observation
        last_obs = timeline().find_n("observed",0) # n-back of 0
        assert len(last_obs) == 1, "You have more than one last observation"

        self.speech_output = "As of " + last_obs[0].time().humanize() + ", the river was " + last_obs[0].height() + " " + last_obs[0].units()
        

def date_parser(req):
    
    assert len(req.dates)==1, "No idea how to parse datestr for multi-day requests"
    day_offset = (req.dates[0].date() - arrow.utcnow().to(cfg.YOUR_ZONE).date()).days
    # Parse datestr
    if day_offset < -1:
        datestr = "{} days ago".format(-1*day_offset)
    elif day_offset == -1:
        datestr = "Yesterday"
    elif day_offset == 0:
        datestr = "Today"
    elif day_offset == 1:
        datestr = "Tomorrow"
    elif day_offset > 1:
        datestr = "In {} days".format(day_offset)
    
    return datestr


    