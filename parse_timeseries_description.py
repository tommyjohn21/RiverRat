import pdb
import arrow
from en import verb
import humanize
import cfg
import parse_timeseries

def describe(timeseries):
    
    # Extract relevant points
    points = extract_points(timeseries)
    if len(points) < 3 and all([x.tag() == "endpoint" for x in points]):
        description = binary_description(timeseries,points)
        return description
    else:
        # Create verb phrases for each event
        raise ValueError("Descriptions with crests/troughs have not been implemented")
        verb_phrases = [verb_phrase(i,pt) for i,pt in enumerate(points)]
        pdb.set_trace()

def extract_points(ts):
    # Initialize empty points list
    points = list()
    
    # Tag and append endpoints
    [ts.data[i].set_tag('endpoint') for i in [0,-1]]
    [points.append(ts.data[i]) for i in [0,-1]]
    
    # Tag and append crests, troughs
    for tidekey in ["crests","troughs"]:
        for i in range(len(getattr(ts,tidekey))): 
            getattr(ts,tidekey)[i].set_tag(tidekey[0:-1])
            points.append(getattr(ts,tidekey)[i])
    
    # Sort xml data by timepoint
    sortkey = lambda pt: pt.time().timestamp
    points.sort(key=sortkey)

    return points
    
def verb_phrase(i,pt):
    
    if pt.tag() == "endpoint":
        if i == 0:
            phrase = "{} at {} {}".format(format_verb("be",pt),pt.height(),pt.units())
        else:
            phrase = " to {} {}".format(pt.height(),pt.units())        
    elif pt.tag() == "crest":
        phrase = "{} at {} {} on {}".format(format_verb("crest",pt),pt.height(),pt.units(),pt.time().format("dddd"))
    elif pt.tag() == "trough":
        phrase = "{} a minimum of {} {} on {}".format(format_verb("reach",pt),pt.height(),pt.units(),pt.time().format("dddd"))
    
    return phrase

def format_verb(v,dtm):
    
    offset = (dtm.time() - arrow.utcnow()).total_seconds()
    
    if offset < 0:
        conjugated = verb.past(v,person=1)
    elif offset == 0:
        conjugated = verb.present(v)
    elif offset > 0:
        conjugated = "will {}".format(v)
        
    return conjugated
    
def binary_description(timeseries,points):

    # Decide if increase or decrease
    net = float(points[-1].height()) - float(points[0].height())
    
    # Generate description for single day
    if (points[-1].time()-points[0].time()).days == 0:
        
        timestr = generate_timestr(points)
        
        if len(timeseries.data) >3:
            description = "{}, the river {} from {} to {} {}".format(
                timestr,
                format_verb(('rise' if net>0 else 'fall'),points[0]),
                points[0].height(),
                points[-1].height(),
                points[0].units())
        elif len(timeseries.data) > 1:
            description = "{}, the river {} {}. However, data for the requested time period is incomplete".format(
                timestr,
                format_verb('be',points[0]),
                timeseries.range.humanize())
        elif len(timeseries.data) == 1:
            raise ValueError("Speech output for a single measurement is not yet implemented")
            description = "{}, the river {} {} {}. However, data for the requested time period is incomplete".format(
                timestr,
                format_verb('be',points[0]),
                points[0].height(),
                points[0].units())
                    
    else:
        
        raise ValueError("Descriptions for multiday intervals are not supported")

    return description

def generate_timestr(points):        

    # Decide which humanizer to use
    day_offset = (points[-1].time().date() - arrow.utcnow().to(cfg.YOUR_ZONE).date()).days
    day_id = arrow.utcnow().to(cfg.YOUR_ZONE).weekday()
    
    if day_offset == 0:
        raise ValueError("Descriptions for today are not supported")
    elif day_offset in [-1,1]:
        timestr = humanize.naturalday(points[-1].time()).capitalize()
    elif day_offset > 7 and day_id == 6:
        timestr = "{} {}".format("On",points[0].time().format("dddd, MMMM Do"))
    elif day_id in range(4) and day_offset > 0:
        timestr = "{} {}".format(("On" if day_id + day_offset < 6 else "Next"),points[0].time().format("dddd"))
    elif day_id in [4,5] and day_offset > 0:
        timestr = "{} {}".format(("On" if day_offset < 4 else "Next"),points[0].time().format("dddd"))
    elif day_id == 6 and day_offset > 0:
        if day_offset < 7:
            timestr = "{} {}".format("On",points[0].time().format("dddd"))        
        elif day_offset == 7:
            timestr = "{} {}".format("Next",points[0].time().format("dddd"))
    elif day_offset < 0:
        timestr = "{} {}".format("On",points[0].time().format("dddd"))      
    
    return timestr
        
    

    