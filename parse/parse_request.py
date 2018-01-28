import pdb
import arrow
import cfg

class date():
    def __init__(self,date):
        if 'W' in date['value']:
            raise ValueError("Can't handle week inputs yet")
        else:
            self.dates = [arrow.get(date['value']).replace(tzinfo=cfg.YOUR_ZONE).to("UTC")]