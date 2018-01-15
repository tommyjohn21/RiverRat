# -*- coding: utf-8 -*-

# Import packages
import pdb
import helpers as hs
import cfg

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
    last_obs = past.datum("obs",0) # n-back of 0
    speech_output = "As of " + last_obs.get_timestr() + ", the river was " + last_obs.height + " " + last_obs.units

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
