import pdb
import arrow
from en import verb
import cfg

def describe(timeseries):

    # Extract relevant points
    points = extract_points(timeseries)

    # Generate description of points
    description = n_ary_description(timeseries,points,0,'')
    print description
    timeseries.plot()

    return description

def extract_points(ts):
    
    # Assert more than one time point--if not, code below runs into uniqueness issues!
    assert len(ts.data) > 1, "You need more than one data point"
    
    # Initialize empty points list
    points = list()
    
    # Tag and append endpoints
    [ts.data[i].set_tag(['endpoint']) for i in [0,-1]]
    [points.append(ts.data[i]) for i in [0,-1]]
    
    # Tag and append crests, troughs
    for tidekey in ["crests","troughs"]:
        for i in range(len(getattr(ts,tidekey))):
            # Append crest/trough moniker to tag
            getattr(ts,tidekey)[i].set_tag(getattr(ts,tidekey)[i].tag() + [tidekey[0:-1]])            
            # Add new point if it hasn't already been tagged as endpoing, etc
            if len(getattr(ts,tidekey)[i].tag())==1:
                points.append(getattr(ts,tidekey)[i])
    
    # Sort xml data by timepoint
    sortkey = lambda pt: pt.time().timestamp
    points.sort(key=sortkey)

    return points

def format_verb(v,dtm):
    
    offset = (dtm.time() - arrow.utcnow()).total_seconds()
    
    if offset < 0:
        conjugated = verb.past(v,person=1)
    elif offset == 0:
        conjugated = verb.present(v)
    elif offset > 0:
        conjugated = "will {}".format(v)
        
    return conjugated
    
def n_ary_description(timeseries,points,current_phrase,description):
    
    # Assert we have single day info
    assert len(set([x.time().date() for x in points])) == 1, "Multiday intervals are not supported!"
    
    if current_phrase < len(points)-1:
        # Find net change for current phrase
        net = change(points,current_phrase)
    
        # Choose verb based on net (since this is human readable)
        verb = change_verb(net)

        # Find type of point (another major control point)
        ty = find_type(points[current_phrase])

        if current_phrase == 0:

            # Initialize string
            timestr = generate_timestr(points)
            description = description + "{}, the river".format(timestr)
        
            if ty == "endpoint":
                description = "{} {} from {} {}".format(description,
                    format_verb(verb,points[current_phrase]),
                    points[current_phrase].height(),
                    points[current_phrase].units())
            else:
                description = "{} {} {} {} and subsequently {}".format(description,
                    format_verb(ty,points[current_phrase]) + " at",
                    points[current_phrase].height(),
                    points[current_phrase].units(),
                    format_verb(verb,points[current_phrase]).replace("will ",""))

            # Recurse
            description = n_ary_description(timeseries,points,current_phrase+1,description)
        
        elif current_phrase == len(points)-2:    
            description = "{} to a {} of {} {}. It {}".format(description,
                ty,
                points[current_phrase].height(),
                points[current_phrase].units(),
                " ".join(["then " + x for x in format_verb(verb,points[current_phrase]).replace("will ","").split(" ") if x != "will"]))    
            # Recurse
            description = n_ary_description(timeseries,points,current_phrase+1,description)
        else:
            raise ValueError("Now you have at least four different events!")
    
    elif current_phrase == len(points)-1:
        
        description = "{} to {} {}".format(description,
            points[current_phrase].height(),
            points[current_phrase].units())
            
        if len(timeseries.data) < 4:
            description = description + ". However, data for this time period is incomplete"
        
    else:
        # This means that current_phrase > len(points)-1... not clear how this would even happen
        raise ValueError("Something has gone terribly wrong")
        
    return description

def generate_timestr(points):        

    # Decide which humanizer to use
    day_offset = (points[-1].time().to(cfg.YOUR_ZONE).date() - arrow.utcnow().to(cfg.YOUR_ZONE).date()).days
    day_id = arrow.utcnow().to(cfg.YOUR_ZONE).weekday()

    if day_offset < -1:
        timestr = "On {}".format(points[0].time().format("dddd"))
    elif day_offset == -1:
        timestr = "Yesterday"
    elif day_offset == 0:
        raise ValueError("Descriptions for today are not supported")
    elif day_offset == 1:
        timestr = "Tomorrow"
    elif day_offset + day_id < 7:
        timestr = "On {}".format(points[0].time().format("dddd"))
    elif day_offset + day_id == 7:
        if day_id < 4:
            timestr = "On {} of next week".format(points[0].time().format("dddd"))
        else:
            timestr = "On {}".format(points[0].time().format("dddd"))
    elif day_offset + day_id < 12:
        if day_id < 5:
            timestr = "On {} of next week".format(points[0].time().format("dddd"))
        else:
            timestr = "On {}".format(points[0].time().format("dddd"))
    else:
        timestr = "On {}".format(points[0].time().format("dddd, MMMM Do"))
        
    return timestr
    
def change(points,i):
    
    # Determine net change between i and i + 1
    net = float(points[i+1].height()) - float(points[i].height())
    
    return net

def change_verb(net):
    
    # Decide whether rise, fall or remain
    if net > 0:
        verb = "rise"
    elif net == 0:
        verb = "be"
        raise ValueError("You need to debug no-change scenario")
    elif net < 0:
        verb = "fall"
    
    return verb
    
def find_type(point):
    
    if len(point.tag()) == 1:
        ty = point.tag()[0]
        return ty
    else:
        point.tag().remove('endpoint')
        if len(point.tag()) == 1:
            ty = point.tag()[0]
            return ty
        else:
            raise ValueError("More than endpoint + 1 other tag was found!")

    

    