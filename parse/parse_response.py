import arrow
import cfg
import parse
import pdb

class look_up_heights:
    def __init__(self,dateslot):

        # Parse request
        self.req = parse.request.date(dateslot)

        # Grab all data
        self.all = parse.timeline().all()
        # Find date matches in the timeseries data

        self.matches = parse.timeseries(self.all).find_data_by_dates(self.req)

        if self.matches is None:
            self.speech_output = "River data is not available for the requested time period"
            return
        else:
            try:
                self.speech_output = self.matches.describe()
            except:
                self.speech_output = "River data cannot be described for this time period"

            
class current_height:
    def __init__(self):
        
        # Grab last observation
        last_obs = parse.timeline().find_n("observed",0) # n-back of 0
        assert len(last_obs) == 1, "You have more than one last observation"

        self.speech_output = "As of " + last_obs[0].time().humanize() + ", the river was " + last_obs[0].height() + " " + last_obs[0].units()
        

# class river_forecast:
#     def __init__(self):
#
#         # Grab all data
#         self.all = timeline().all()
#
#         # Edit all data for 1. most recent observation and 2. all forecasted data
#         self.forecast = timeline().find_n('observed',0)
#         self.forecast.extend(filter(lambda dtm: dtm.key() == "forecast",self.all))
#
#         # Convert xml forecast data to timeseries
#         self.forecast = timeseries(self.forecast)
#
#
#         pdb.set_trace()
#
#         # Find date matches in the timeseries data
#         self.matches = timeseries(self.all).find_data_by_dates(self.req)
#
#         pdb.set_trace()


    