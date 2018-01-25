import pdb
import requests
import xml.etree.ElementTree as ET
import arrow
import cfg
from parse_datum import datum

class timeline:
    def __init__(self):
        # Curl response
        response = requests.get(cfg.XML_BASE)
        
        # Convert for XML parsing to element tree (et)
        response_xml = ET.fromstring(response.text)
        
        # Parse xml to timeline object
        self.observed = response_xml.find("observed")
        self.forecast = response_xml.find("forecast")
        self.sigstages = response_xml.find("sigstages")
    
    def find_n(self,key,n):
        
        # Grab either observations or predictions
        data = getattr(self,key)
        
        # Convert n to list if it is an integer
        if type(n) == int:
            n = [n]
        
        # Now grab match(es)
        matches = list()
        [matches.append(datum(data[i],key)) for i in n]    
        return matches
        
    def all(self):
        
        data = list()
        # Look through observed and forecasted
        for key in ["observed", "forecast"]:
            for dtm in getattr(self,key).findall("datum"):
                dtm = datum(dtm,key)
                data.append(dtm)
            
            # Reverse list to ensure we are going oldest-->latest        
            if key == "observed":
                data.reverse()
        
        return data