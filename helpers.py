# Import packages
import pdb
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from dateutil import tz
import cfg

class datum:
    def __init__(self,key,n):
        # Curl response
        response = requests.get(cfg.XML_BASE)
    
        # Convert for XML parsing to element tree (et)
        et = ET.fromstring(response.text)
        
        # Determine if you are looking forward or backward
        if key == "obs":
            key_str = "observed"
        elif key == "pred":
            key_str = "forecast"
        
        # Get nth datum
        dtm = get_datum(et,key_str,n)
        
        # Embed direction
        self.key = key
        
        # Observation time in your timezone
        self.time = get_time(dtm)
    
        # Observation height
        self.height, self.units = get_height(dtm)
    
    def get_timestr(self):
        # Human readable timestamp

        # Get current time in YOUR_ZONE
        ## Initialize datetime.now as UTC
        now_time = convert_timezone(datetime.now(tz.tzutc()))

        # Determine the clock time at dt
        clockstr = self.time.strftime('%I').lstrip("0") + ('' if  len(self.time.strftime('%M').lstrip("0"))==0 else self.time.strftime(' %M').lstrip("0")) + (' AM' if int(self.time.strftime('%H'))<12 else ' PM')

        # Find day difference
        delta = now_time.date() - self.time.date()
        
        if delta.days > 1:
            timestr = 'last ' + self.time.strftime('%A') + ' at ' + clockstr
        elif delta.days == 1:
            timestr = "yesterday at " + clockstr
        elif delta.days == 0:
            timestr = "today at " + clockstr
        elif delta.days == -1:
            timestr = "tomorrow at " + clockstr
        elif delta.days < -1 and delta.days > -4:
            timestr = 'this coming ' + self.time.strftime('%A') + ' at ' + clockstr
        elif delta.days <= -4:
            timestr = 'next ' + self.time.strftime('%A') + ' at ' + clockstr
        
        return timestr

def get_datum(et,key_str,n):
    dtm = et.find(key_str)
    return dtm[n]
    
def get_time(dtm):
    
    # Get initial timestamp from ob
    time = dtm[0].text
    # Convert string to datetime
    time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S-00:00')
    
    # Return in appropriate timezone
    return convert_timezone(time)

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

def convert_timezone(time):

    # Timezone defs (assuming from_zone is UTC)
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz(cfg.YOUR_ZONE)

    # Declare time as UTC
    time_utc = time.replace(tzinfo=from_zone)

    # Convert timezone
    return time_utc.astimezone(to_zone)
    