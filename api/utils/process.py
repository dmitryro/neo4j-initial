import logging
import asyncio
from flask import make_response
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
        logger.info("CASE 111 ----------------------------------")
        if '_permanent' in action['selected_options'][0]['value']:
            value = action['selected_options'][0]['value']
        else:
            value = ""
    else:
        logger.info("CASE 222 ----------------------------------")
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

    state_data = {"container": slack_request["container"], "answer_id": value}

    if action["action_id"] == "answer_action":
        return make_response()
    return make_response("Unable to process action", 400)


def process_dialogs():
    pass
