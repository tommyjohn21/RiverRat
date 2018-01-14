# Import packages
import pdb
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from dateutil import tz

class obs:
    def __init__(self,XML_BASE,nback,YOUR_ZONE):
        # Curl response
        response = requests.get(XML_BASE)
    
        # Convert for XML parsing to element tree (et)
        et = ET.fromstring(response.text)
    
        # Get last observation
        ob = get_observation(et,nback)
        
        # Put last time at datetime object in correct zone
        self.time = get_time(ob,'UTC',YOUR_ZONE)

        # Human readable last time
        self.timestr = time_since(self.time,YOUR_ZONE)
    
        # Get last height
        self.height, self.units = get_height(ob)

def get_observation(et,nback):
    obs = et.find("observed")
    return obs[nback]
    
def get_time(ob,from_zone,to_zone):
    
    # Get initial timestamp from et
    time = ob[0].text
    # Convert string to datetime
    time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S-00:00')
    
    # Return in appropriate timezone
    return convert_timezone(time,from_zone,to_zone)

def get_height(ob):
    
    # Get height
    height = ob[1].text
    
    # Check units
    units = ob[1].get('units')
    if units != 'ft':
        raise ValueError("Data is not in feet")
    else:
        units = 'feet'
        
    return height, units

def convert_timezone(time,from_zone,to_zone):
    
    # Timezone defs
    from_zone = tz.gettz(from_zone)
    to_zone = tz.gettz(to_zone)
    
    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    time_utc = time.replace(tzinfo=from_zone)
    
    return time_utc.astimezone(to_zone)

def time_since(dt,YOUR_ZONE):
    
    # Get current time in YOUR_ZONE
    now_time = convert_timezone(datetime.now(tz.tzutc()),'UTC',YOUR_ZONE)
    
    # Determine the clock time at dt
    clockstr = dt.strftime('%I').lstrip("0") + ('' if  len(dt.strftime('%M').lstrip("0"))==0 else dt.strftime(' %M').lstrip("0")) + (' AM' if int(dt.strftime('%H'))<12 else ' PM')
    
    # Find day difference
    delta = now_time.date() - dt.date()
    if delta.days == 0:
        timestr = "today at " + clockstr
    elif delta.days == 1:
        timestr = "yesterday at " + clockstr
    else:
        timestr = str(delta.days) + ' days ago'
    
    return timestr
    