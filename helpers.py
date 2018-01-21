# Import packages
import pdb
import requests
import xml.etree.ElementTree as ET
import arrow
import math
import cfg

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
        self.req = arrow.get(date['value'])
        
        # Find data for days listed in req
        self.data = get_matching_data(self.req)
        
    def min(self):
        # Find the minimum of the data_array
        return min([float(d.height) for d in self.data])
         
    def max(self):
        # Find the minimum of the data_array
        return max([float(d.height) for d in self.data])

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
    
def get_timeline(et):

    # Harvest all data
    timeline = dict()
    for key in ["observed","forecast"]:
        timeline[key] = list()
        for dtm in et.find(key).findall("datum"):
            timeline[key].append(get_time(dtm))

    # Return timeline
    return timeline
    
def get_matching_data(req):
    
    # Curl response
    response = requests.get(cfg.XML_BASE)
    
    # Convert for XML parsing to element tree (et)
    et = ET.fromstring(response.text)
    
    # Process timeline
    timeline = get_timeline(et)
    
    # Parse out indices of the correct dates
    idx = dict()
    for key in ["observed","forecast"]:
        dates = [time.date() for time in timeline[key]]
        idx[key] = []
        for i,d in enumerate(dates):
            if d == req.date():
                idx[key].append(i)
    
    # Grab the actual data points
    data = list()
    for key in ["observed","forecast"]:
        for i in idx[key]:
            data.append(datum(key,i))
    
    # Output the correct list  
    return data
        
    