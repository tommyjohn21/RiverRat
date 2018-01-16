# Import packages
import pdb
import requests
import xml.etree.ElementTree as ET
import arrow
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
        
        # Observation time
        self.time = get_time(dtm)
    
        # Observation height
        self.height, self.units = get_height(dtm)

def get_datum(et,key_str,n):
    dtm = et.find(key_str)
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
    