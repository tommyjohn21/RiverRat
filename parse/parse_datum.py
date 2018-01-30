import pdb
import arrow
import xml.etree.ElementTree as ET
import cfg

class datum:
    def __init__(self,xml,key):
        
        # Load xml
        self.xml = xml
        
        # Add key to xml
        self.xml.append(ET.Element('key'))
        self.xml[-1].text = key
        
        # Initialize open element container "tag" for use labeleing crests, troughs and endpoints (see parse_timeseries_description)
        self.xml.append(ET.Element('tag'))
        self.xml[-1].text = []
        
    def time(self):
        # Get initial timestamp from datum
        time = self.xml.find('valid').text
    
        # Convert string to arrow time object
        time = arrow.get(time,'YYYY-MM-DDTHH:mm:ss-00:00')
    
        # Verify timezone is UTC
        assert self.xml.find('valid').get('timezone') == time.tzinfo.tzname(0), "Time zones don't match"
        assert time.tzinfo.tzname(0) == "UTC", "Time zone is not UTC"
        
        time = time.to(cfg.YOUR_ZONE)
    
        return time
    
    def height(self):
        
        # Get height
        height = self.xml.find('primary').text
        assert self.xml.find('primary').get('units') == "ft", "Data is not in feet"
        
        return height
        
    def key(self):
        
        # Get key
        key = self.xml.find('key').text
        
        return key
        
    def set_tag(self,t):
        
        # Set tag
        self.xml.find('tag').text = t
    
    
    def tag(self):
        
        # Get tag
        tag = self.xml.find('tag').text
        
        return tag
        
    def units(self):
        
        # Set units; you asserted feet when measuring height
        units = "feet"
        
        return units