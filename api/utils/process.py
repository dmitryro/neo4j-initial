import logging
import asyncio
from flask import jsonify,  make_response
from flask_api import status
import json
import os
from redis import StrictRedis as RegularStrictRedis
from slack import WebClient
import websockets
from kafka import KafkaProducer

logger = logging.getLogger(__name__)
read_env = lambda property: os.environ.get(property, None)
producer = KafkaProducer(bootstrap_servers='kafka:9092') 
                         #value_serializer=lambda v: json.dumps(v).encode('utf-8'), 
                         #key_serializer=lambda v: json.dumps(v).encode('utf-8'))


SLACK_TOKEN = read_env('SLACK_TOKEN')

redis = dict()
redis['db'] = read_env('REDIS_DB')
redis['host'] = read_env('REDIS_HOST')
redis['port'] = read_env('REDIS_PORT')
r = RegularStrictRedis(**redis)

def redis_store(msg, key):
    r.lpush(key, msg)


def process_block_actions(slack_request: dict):
    """
    Slack Action processor.

    Here we are going to process decoded slack request "block actions"
    https://api.slack.com/reference/messaging/blocks#actions

    Example request: example-data/block_action.json

    We will present user with 2 buttons.
    1. Open dialog - which contains standup questions
    2. Skip today - to let user pass the meeting

    Returns
    -------
    flask.Response
        Empty response 200 signifies success.

    """
    msg = json.dumps(slack_request).encode('utf-8')
        
    action = slack_request["actions"][0]
    if action.get('selected_options', None):
        if '_permanent' in action['selected_options'][0]['value']:
            value = action['selected_options'][0]['value']
            producer.send('make_permanent', key=bytes(msg), value=bytes(msg))
        else:
            value = ""
    else:
        if action['type']=='checkboxes' and len(action['selected_options'])==0:
            producer.send('make_nonpermanent', key=bytes(msg), value=bytes(msg))
        else:
            value = action["selected_option"]["value"] 
            logger.info(f"THIS IS OUR CASE IN API {slack_request}")

            if 'approve_' in value: 
                redis_store(msg, 'approve')
                producer.send('approve', key=bytes(msg), value=bytes(msg))
            elif 'dismiss_' in value:
                redis_store(msg, 'dismiss')
                producer.send('dismiss', key=bytes(msg), value=bytes(msg)) 
            elif 'edit_' in value:
                redis_store(msg, 'edit')
                producer.send('edit', key=bytes(msg), value=bytes(msg))    
            else:
                producer.send('dismiss', key=bytes(msg), value=bytes(msg))


    #if action["action_id"]: == "answer_action":
    result = {} 
    return make_response(jsonify(result), status.HTTP_204_NO_CONTENT)


def process_dialogs(slack_request: dict):
    msg = json.dumps(slack_request).encode('utf-8')
    producer.send('submit_edited', key=bytes(msg), value=bytes(msg))   
    logger.info("Sent Kafka topic message")
    result = {}
    return make_response(jsonify(result), status.HTTP_204_NO_CONTENT)

