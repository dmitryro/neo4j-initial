# -*- coding: utf-8 -*-
import base64
from contextlib import contextmanager
import json
import logging
import os
from redis import StrictRedis as RegularStrictRedis
from aredis import StrictRedis as AsyncStrictRedis
import requests
from six.moves import _thread, range, queue
import six
from slack import WebClient
from slack.errors import SlackApiError
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
import tempfile
from time import sleep

logger = logging.getLogger(__name__)
read_env = lambda property: os.environ.get(property, None) 
default_answer = read_env("SLACK_DEFAULT_ANSWER")
client = WebClient(token=read_env("SLACK_TOKEN"))

redis = dict()
redis['db'] = read_env('REDIS_DB')
redis['host'] = read_env('REDIS_HOST')
redis['port'] = read_env('REDIS_PORT')
r = RegularStrictRedis(**redis)
ar = AsyncStrictRedis(**redis)

def obtain_session():
    """ Get SQLAlchemy session """
    engine = create_engine(os.environ['DATABASE_URL'])
    session = sessionmaker(autoflush=True)
    # Bind the sessionmaker to engine
    session.configure(bind=engine)
    return session()


def read_blocks(text=None, question=None, answer=default_answer):

    if question:
        blocks = [{"type": "section",
                   "block_id": "section 890",
                   "text": {
                       "type": "mrkdwn",
                       "text": text
                    },
                  },
                  {"type": "section",
                   "block_id": "section 891",
                   "text": {
                       "type": "mrkdwn",
                       "text": question
                    }
                   },

                   {
                         "type": "divider",
                         "block_id": "divider1"
                   },
 
                  {"type": "section",
                   "block_id": "section 892",
                   "text": {
                       "type": "mrkdwn",
                       "text": "The proposed answers:"
                    }
                   },


                   {
                       "type": "section",
                       "text": {
                            "type": "mrkdwn",
                            "text": answer
                        },
                       "accessory": {
                            "type": "overflow",
                            "action_id": "answer_action",
                            "options":[
                                         {
                                            "text": {
                                                  "type": "plain_text",
                                                  "text": "Approve",
                                            },
                                            "value": f"approve_{encode(answer)}"
                                         },
                                         {
                                            "text": {
                                                  "type": "plain_text",
                                                  "text": "Dismiss"
                                            },
                                            "value": f"dismiss_{encode(answer)}"
                                         },
                                         {
                                            "text": {
                                                  "type": "plain_text",
                                                  "text": f"Edit"
                                            },
                                            "value": f"edit_{encode(answer)}"
                                         }
                               ] # Options end
                          } # Accessory end
                    } # Section end

      ]


    else:
        blocks = [{"type": "section",
                   "block_id": "section 890",
                   "text": {
                       "type": "mrkdwn",
                       "text": text
                    },
                  },
                  {"type": "actions",
                   "block_id": "actions1",
                   "elements": [
                                    {
                                        "type": "button",
                                        "text": {
                                             "type": "plain_text",
                                             "text": "Approve"
                                        },
                                        "value": "approve",
                                        "action_id": "button_1"
                                    },
                                    {
                                        "type": "button",
                                        "text": {
                                             "type": "plain_text",
                                             "text": "Dismiss"
                                        },
                                        "value": "dismiss",
                                        "action_id": "button_2"
                                    }
                       ]
                  }
                 ]
     
#,
#                "accessory": {
#                    "type": "overflow",
#                    "options": [{"text": {"type": "plain_text",
#                                          "text": "Approve"
#                                         },
#                                 "value": "value-0"
#                                },
#                                {"text": {"type": "plain_text",
#                                          "text": "Skip"
#                                         },
#                                 "value": "value-1"
#                                },
#                                {"text": {"type": "plain_text",
#                                          "text": "Make a Q/A"
#                                         },
#                                 "value": "value-2"
#                                },
#                                {"text": {"type": "plain_text",
#                                          "text": "Create a ticket"
#                                         },
#                                         "value": "value-3"
#                                },
#                                {"text": {"type": "plain_text",
#                                          "text": "Store"
#                                         },
#                                 "value": "value-4"
#                                },
#                                {"text": {"type": "plain_text",
#                                          "text": "Edit"
#                                         },
#                                 "value": "value-5"
#                                },
#                                {"text": {"type": "plain_text",
#                                          "text": "Delete"
#                                         },
#                                 "value": "value-6"
#                                 }
#                                ],
#                               "action_id": "overflow"
#                             }
#                        }
#                    ]

    return blocks


def respond_next(answer, question, user, channel_id, action='approve'):
    if action == 'approve':
        try:
            user_id = user['id']
            username = user['username']
            response = client.chat_postMessage(
                        channel=channel_id,
                        user=user_id,
                        as_user=True,
                        icon_emoji=":chart_with_upwards_trend:",
                        text=f'Hi <@{user_id}>! {answer}"',
                        username=username,
                        thread_ts=None)
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            logger.error(f"Got an error in respond approved : {e.response['error']}")

    elif action == 'dismiss':
        try:
            user_id = user['id']
            username = user['username']
            response = client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                as_user=False,
                icon_emoji=":chart_with_upwards_trend:",
                text=f'Hi admin, you dismissed: {answer}',
                username='kbpro',
                thread_ts=None #thread_ts 
            ) 


        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            logger.error(f"Got an error in respond approved : {e.response['error']}")
        
    elif action == 'edit':
        try: 
            user_id = user['id']
            username = user['username']
            
            response = client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                as_user=False,
                icon_emoji=":chart_with_upwards_trend:",
                text=f'Hi admin, please edit: {answer}',
                username='kbpro',
                thread_ts=None #thread_ts 
            )  
 
        except SlackApiError as e: 
            # You will get a SlackApiError if "ok" is False 
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found' 
            logger.error(f"Got an error in respond approved : {e.response['error']}")      

    else:
        pass

def respond(payload, text=None, question=None, answer=default_answer,  ephemeral=False):
    data = payload['data']
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']
    channel_id = data['channel']
    thread_ts = data['ts']
    user = data['user']
    logger.info(f"STEP 2 IN RESPOND HERE IS WHAT OUR USER IS LIKE {user}")
    logger.info(f"==========+> WE ARE IN RESPOND SO FAR {text}  {question}   {answer} ")
    try:
        if (ephemeral):
            response = web_client.chat_postEphemeral(
                channel=channel_id,
                user=user,
                as_user=False,
                icon_emoji=":chart_with_upwards_trend:",
                #text=text,
                username='kbpro',
                blocks=read_blocks(text=text, answer=answer, question=question),
                thread_ts=None #thread_ts
            )
        else:  
            response = web_client.chat_postMessage(
                channel=channel_id,
                as_user=False,
                user=user,
                username='kbpro',
                icon_emoji=":chart_with_upwards_trend:",
                text=f"Hi <@{user}>! {text}",
                thread_ts=None #thread_ts
            )
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        assert e.response["ok"] is False
        assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
        logger.error(f"Got an error: {e.response['error']}")


def save_pending(pending):
    s = obtain_session()
    s.add(pending)
    s.commit()


def encode(message):
    if not message:
        return ""
    message_bytes = message.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('utf-8')
    return base64_message


def decode(base64_message):
    base64_bytes = base64_message.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    message = message_bytes.decode('utf-8')
    return message


async def read_approved():
    approved = []
    while(await ar.llen('approved')!=0):
        item = await ar.lpop('approved')
        d = json.loads(item)
        approved.append(d)  
    return approved


def store_answer(question, answer):
    msg = {'question': question, "answer": answer}
    r.lpush('answered', json.dumps(msg).encode('utf-8'))
    logger.info(f"Storing answered in NEO4J - {question} {answer}")


def extend_answer(question, answer, extention):
    msg = {'question': question, "answer": answer, "extentions": extension}
    r.lpush('extended', json.dumps(msg).encode('utf-8'))
    logger.info(f"Storing extanded answer  in NEO4J - {question} {answer} {extension}")


def edit_answer(question, answer):
    logger.info(f"===================== > > > I AM ABOUT TO EDIT {question}, {answer}")
    msg = {'question': question, "answer": answer}
    r.lpush('edited', json.dumps(msg).encode('utf-8'))
    logger.info(f"Storing edited answer  in NEO4J - {question} {answer}")


def read_question(msg):
    if not msg:
        return 'Empty question sent, sorry'
    answer = {"answer": msg}
    r.lpush('searched_questions', json.dumps(answer).encode('utf-8'))
    logger.info("Looking for question")
    sleep(4)

    key = encode(msg)    
    question_key = '{key}-question'
    question = r.get(question_key)
    if not question:
        return None
    else:
        return question.decode('utf-8')



def read_answer(msg):
    if not msg:
        return default_answer
    elif msg == default_answer:
        return default_answer

    r.lpush('questions', msg)
    logger.info("Processing answer")
    sleep(4)
    key = encode(msg)
    answer_key = f'{key}-answer'
    answer = r.get(answer_key)
 
    if not answer:
        return default_answer
    elif answer == default_answer:
        return default_answer
    else:
        return answer.decode('utf-8')







