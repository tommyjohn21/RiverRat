# Import packages
import pdb
import requests
import xml.etree.ElementTree as ET
import arrow
import math
import cfg
import aniso8601

class datum:
    def __init__(self,key,n):
        # Curl response
        response = requests.get(cfg.XML_BASE)
        
        # Convert for XML parsing to element tree (et)
        et = ET.fromstring(response.text)
        
        # Get nth datum
        dtm = get_datum(et,key,n)

        # Embed direction
        self.key = key
        
        # Observation time
        self.time = get_time(dtm)
    
        # Observation height
        self.height, self.units = get_height(dtm)
        
class data_array:
    def __init__(self,date):
        
        # Get turn requested time into arrow time object
        self.req, self.datestr = date_parser(date)
        
        # Find data for days listed in req
        self.heights, self.units, self.key = get_matching_data(self.req)

    def min(self):
        # Find the minimum of the data_array
        return min([float(d) for d in self.heights])
         
    def max(self):
        # Find the minimum of the data_array
        return max([float(d) for d in self.heights])
        
    def humanize(self):
        
        # Humanize data
        if self.key == "forecast":
            human_string = self.datestr + ", the river is predicted to be between " + str(self.min()) + " and " + str(self.max()) + " feet"
        elif self.key == "observed":
            human_string = self.datestr + ", the river was observed to be between " + str(self.min()) + " and " + str(self.max()) + " feet"
        elif self.key == "both":
            human_string = "Based on " + self.datestr.lower() + "'s observations and forecasted predictions, the river should be between " + str(self.min()) + " and " + str(self.max()) + " feet"
            
        return human_string

def get_datum(et,key,n):
    dtm = et.find(key)
    return dtm[n]
    
def get_time(dtm):
    
    # Get initial timestamp from datum
    time = dtm[0].text
    
    # Convert string to arrow time object
    time = arrow.get(time,'YYYY-MM-DDTHH:mm:ss-00:00')
    
    # Verify timezone is UTC
    assert dtm[0].get('timezone') == time.tzinfo.tzname(0), "Time zones don't match"
    assert time.tzinfo.tzname(0) == "UTC", "Time zone is not UTC"
    
    return time

def get_height(dtm):
    
    # Get height
    height = dtm[1].text
    
    # Check units
    units = dtm[1].get('units')
    if units != 'ft':
        raise ValueError("Data is not in feet")
    else:
        units = 'feet'
        
    return height, units
    
def parse_timeline(et,req):

    # Harvest all matching data
    matching_data = list()
    keys = list()
    for key in ["observed","forecast"]:
        for i,dtm in enumerate(et.find(key).findall("datum")):
            if get_time(dtm).to(cfg.YOUR_ZONE).date()==req.date():
                matching_data.append(get_height(dtm))
                keys.append(key)

    # Return timeline
    return matching_data, keys
    
def get_matching_data(req):

    # Curl response
    response = requests.get(cfg.XML_BASE)
    
    # Convert for XML parsing to element tree (et)
    et = ET.fromstring(response.text)
    
    # Process timeline and return data where the date matches
    matching_data,keys = parse_timeline(et,req)
    
    # Separate units from heights
    heights = [d[0] for d in matching_data]
    assert all([d[1]=="feet" for d in matching_data])
    units = "feet"
    
    # Key processing
    if all(k=="forecast" for k in keys):
        key = "forecast"
    elif all(k=="observed" for k in keys):
        key = "observed"
    else:
        key = "both"

    # Output the correct list  
    return heights, units, key
    
def date_parser(date):
    
    if 'W' in date['value']:
        raise ValueError("Can't handle week inputs yet")
    else:
        date = arrow.get(date['value']).replace(tzinfo=cfg.YOUR_ZONE)
        day_offset = (date.date() - arrow.utcnow().to(cfg.YOUR_ZONE).date()).days
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
        
    return date, datestr
        
    