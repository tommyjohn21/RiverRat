# -*- coding: utf-8 -*-

# Import packages
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from dateutil import tz
import pdb
import math

# Base for river heights
XML_BASE="http://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=evvi3&output=xml"

def handler(event, context):
        
        # Authenticate the application for incoming request
        if (event["session"]["application"]["applicationId"] !=
                "amzn1.ask.skill.2741149f-5d26-46d2-901b-48e72b7ca7c4"):
            raise ValueError("Invalid Application ID")
        
        if event["session"]["new"]:
            on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

        if event["request"]["type"] == "LaunchRequest":
            return on_launch(event["request"], event["session"])
        elif event["request"]["type"] == "IntentRequest":
            return on_intent(event["request"], event["session"])
        elif event["request"]["type"] == "SessionEndedRequest":
            return on_session_ended(event["request"], event["session"])

def on_session_started(session_started_request, session):
    print("Starting new session.")

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "CurrentHeight":
        return current_height()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print("Ending session.")
    # Cleanup goes here...

def handle_session_end_request():
    card_title = "HowHigh"
    speech_output = "Enjoy the river!"
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "HowHigh"
    speech_output = "What would you like to know?"
    reprompt_text = "You can ask: how high is the river?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def current_height():
    session_attributes = {}
    card_title = "How high is the Ohio river?"
    reprompt_text = ""
    should_end_session = True

    # Curl response
    response = requests.get(XML_BASE)

    # Convert for XML parsing
    response = ET.fromstring(response.text)
    
    # Parse river height out
    obs = response.find("observed")
    last_obs = obs[0]
    
    last_time = last_obs[0].text
    # Change over time zone
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/Chicago')
    
    # utc = datetime.utcnow()
    last_time_utc = datetime.strptime(last_time, '%Y-%m-%dT%H:%M:%S-00:00')
    now_time_utc = datetime.now(tz.tzutc())

    # Tell the datetime object that it's in UTC time zone since 
    # datetime objects are 'naive' by default
    last_time_utc = last_time_utc.replace(tzinfo=from_zone)
    now_time_utc = now_time_utc.replace(tzinfo=from_zone)

    # Convert time zone
    last_time_central = last_time_utc.astimezone(to_zone)
    now_time_central = now_time_utc.astimezone(to_zone)
    
    # Get height
    last_height = last_obs[1].text
    
    units = last_obs[1].get('units')
    if units != 'ft':
        raise ValueError("Data is not in feet")
    else:
        units = 'feet'
    
    if now_time_central.date() == last_time_central.date():
        pm = math.floor((last_time_central.hour)/12)
        if pm == 0:
            pm = " AM"
        elif pm == 1:
            pm = ' PM'
        timestr = 'today at ' + str(last_time_central.hour%12) + (' ' + str(last_time_central.minute) if last_time_central.minute > 0 else '') + pm
    else:
        delta = datetime.today().date() - last_time_central.date()
        if delta.days == 1:
            pm = math.floor((last_time_central.hour)/12)
            if pm == 0:
                pm = " AM"
            elif pm == 1:
                pm = ' PM'
            timestr = 'yesterday at ' + str(last_time_central.hour%12) + (' ' + str(last_time_central.minute) if last_time_central.minute > 0 else '') + pm
        else:
            timestr = str(delta.days) + ' days ago'

    speech_output = "As of " + timestr + ", the river was " + last_height + " feet"

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
