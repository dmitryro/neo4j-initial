# -*- coding: utf-8 -*-
import shortuuid
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
bot_token=read_env("SLACK_TOKEN")
user_token=read_env('SLACK_USER_TOKEN')
client = WebClient(token=bot_token)

redis = dict()
redis['db'] = read_env('REDIS_DB')
redis['host'] = read_env('REDIS_HOST')
redis['port'] = read_env('REDIS_PORT')
r = RegularStrictRedis(**redis)
ar = AsyncStrictRedis(**redis)

def get_uuid():
    shortuuid.set_alphabet("abcdefghijklmnopqrstuvwxyz0123456789")
    return shortuuid.uuid()

def encode(message):
    if not message:
        return ""
    message_bytes = message.encode('utf-8')
    base64_bytes = base64.a85encode(message_bytes)
    base64_message = base64_bytes.decode('utf-8')
    return str(base64_message)


def decode(base64_message):
    base64_bytes = base64_message.encode('utf-8')
    message_bytes = base64.a85decode(base64_bytes)
    message = message_bytes.decode('utf-8')
    return str(message)


def obtain_session():
    """ Get SQLAlchemy session """
    engine = create_engine(os.environ['DATABASE_URL'])
    session = sessionmaker(autoflush=True)
    # Bind the sessionmaker to engine
    session.configure(bind=engine)
    return session()


def read_modal(answer, index):
    modal={
        "type": "modal",
        "callback_id": f"modal-id-{index}",
        "title": {
            "type": "plain_text",
            "text": "Edit Answer"
        },
        "submit": {
            "type": "plain_text",
            "text": "Submit"
        },
        "close": {
            "type": "plain_text",
            "text": "Cancel"
        },
        "blocks": [
            {
            "type": "input",
            "block_id": f"b-id",
            "label": {
                "type": "plain_text",
                "text": "Edit Answer",
            },
            "element": {
                "action_id": f"a-id-{index}",
                "type": "plain_text_input",
                "action_id": "ml_input",
                "multiline": True,
                "placeholder": {
                        "type": "plain_text",
                        "text": answer
                },
                "initial_value": answer
            }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": " "
                },
                "accessory": {
                    "type": "checkboxes",
                    "options": [
                        {
                            "text": {
                                "type": "mrkdwn",
                                "text": "Make this change permanent"
                            },
                            "value": "value_permanent"
                        }
                    ]
                }
            }
        ]
        }
    return modal


def read_answer_block(ans, index):
    answer = decode(list(ans.keys())[0])
    uuid = list(ans.values())[0]
    approve_key = f"approve_{uuid}"
    dismiss_key = f"dismiss_{uuid}"
    edit_key = f"edit_{uuid}"
    delete_key = f"delete_{uuid}"
    qa_key = f"qa_{uuid}"

    block = {"type":"section",
             "text": {
                       "type": "mrkdwn",
                       "text":  str(answer) 
              },
              "accessory": {
                  "type": "overflow",
                  "action_id": f"answer_action",
                  "options":[
                      {
                        "text": {
                            "type": "plain_text",
                            "text": "Approve",
                        },
                        "value": approve_key
                      },
                      { 
                        "text": {
                            "type": "plain_text",
                            "text": "Dismiss",
                        },
                        "value": dismiss_key
                      },
                      {
                        "text": {
                            "type": "plain_text",
                            "text": "Edit",
                        },
                        "value": edit_key
                      },
                      {
                        "text": {
                            "type": "plain_text",
                            "text": "Delete",
                        },
                        "value": delete_key
                      },
                      {
                        "text": {
                            "type": "plain_text",
                            "text": "Make it Q/A",
                        },
                        "value": qa_key
                      }
                  ] # Options end
              } # Accessory end
            }
    return block


def read_blocks(text=None, question=None, answers=[{encode(default_answer):get_uuid()}]):
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
                   }
        ]

        for i, answer in enumerate(answers):
            b = read_answer_block(answer, i)
            blocks.append(b)
        return blocks
    else:
        blocks = [{"type": "section",
                   "block_id": "section 890",
                   "text": {
                       "type": "mrkdwn",
                       "text": text
                    },
                  }
                 ]
     
    return blocks


def delete_ephemeral(channel_id, message_ts):
    token=read_env("SLACK_TOKEN")
    try:
        client.chat_delete(token=token,
                           channel=channel_id,
                           ts=message_ts)    
        logger.info(f"Deleted ephemeral message from channel {channel_id} with timestamp {message_ts}")
    except Exception as e:
        logger.error(f"Failed deleting ephemeral message from channel {channel_id} with timestamp {message_ts}")
        
def confirm_blocks(text, uuid):
    approve_key = f"approve_{uuid}"
    blocks = [{
              "type": "section",
              "text": {
                  "type": "mrkdwn",
                  "text": text
              },
              "accessory": {
                  "type": "button",
                  "text": {
                      "type": "plain_text",
                      "text": "Post"
                  },
                  "value": approve_key,
                  "action_id": "answer_action"
              }
             }]
    return blocks


def respond_next(answer:str, uuid:str, question:str, answers:list, user:dict, channel_id:str, 
                trigger_id:str, message_ts:str, index:int, action='approve'):

    token=read_env("SLACK_TOKEN")
    if action == 'approve':
        try:
            user_id = user['id']
            username = user['username']
            response = client.chat_postMessage(
                        channel=channel_id,
                        user=user_id,
                        as_user=True,
                        icon_emoji=":chart_with_upwards_trend:",
                        text=f'Hi <@{user_id}>! {answer}',
                        username=username,
                        thread_ts=None)
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            logger.error(f"Got an error in respond approved : {e.response['error']}")
    elif action == 'confirm':
        try:
            logger.info(f"2.OUR DEAR USER ! {user}")
            logger.info("Updating the message ...")
            #response = client.chat_update(
            #    token=bot_token,
            #    channel=channel_id,
            #    #blocks=blocks,
            #    text="HI",
            #    ts=message_ts,
            #    as_user=True
            #)

            user_id = user['id']
            username = user['username']
            text = f'Hi admin! Edited the answer to the question by the user <@{user_id}> to be "{answer}".'
            blocks = confirm_blocks(text, uuid)
            response = client.chat_postEphemeral(
                channel=channel_id,
                as_user=False,
                user=user_id,
                icon_emoji=":chart_with_upwards_trend:",
                username='kbpro',
                blocks=blocks,
                thread_ts=None #thread_ts
            )

        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            logger.error(f"Got an error in delete {message_ts}: {e.response}")


    elif action == 'dismiss':
        try:
            user_id = user['id']
            username = user['username']
            response = client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                as_user=True,
                icon_emoji=":chart_with_upwards_trend:",
                text=f'Hi admin, you dismissed: {answer}',
                username='kbpro',
                thread_ts=None
            ) 
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            logger.error(f"Got an error in dismissed : {e.response['error']}")
        
    elif action == 'edit':
        try:
            view = read_modal(answer, index)
            user_id = user['id']
            username = user['username']

            api_response = client.views_open(
              token=token,
              trigger_id=trigger_id,
              view=view
            )            
        except SlackApiError as e: 
            # You will get a SlackApiError if "ok" is False 
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found' 
            logger.error(f"Got an error in respond edit : {e} - {e.response['error']} - {e.response['response_metadata']}")      
    elif action == 'qa':
        pass

    elif action == 'pr':
        pass

    elif action == 'jira':
        pass   
    elif action == 'delete':
        try:
            logger.info("Updating the message ...")
            #response = client.chat_update(
            #    token=bot_token,
            #    channel=channel_id,
            #    #blocks=blocks,
            #    text="HI",
            #    ts=message_ts,
            #    as_user=True
            #)
            user_id = user['id']
            username = user['username']
            response = client.chat_postEphemeral(
                channel=channel_id,
                as_user=False,
                user=user_id,
                icon_emoji=":chart_with_upwards_trend:",
                text=f'Hi admin! Deleted the answer "{answer}" to the question by the user <@{user_id}> permanently.',
                username='kbpro',
                thread_ts=None #thread_ts
            )


        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            logger.error(f"Got an error in delete {message_ts}: {e.response}")
    

def respond(payload, text=None, question=None, answers=[{encode(default_answer):get_uuid()}], ephemeral=False):
    data = payload['data']
    channel_id = data['channel']
    thread_ts = data['ts']
    user = data['user']
    logger.info(f"==========> LET US SEE WHAT WHE GOT {user}")
    blocks=read_blocks(text=text, answers=answers, question=question)

    try:
        if (ephemeral):
            user_id = user['id']
            username = user['username']
            response = client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                as_user=False,
                icon_emoji=":chart_with_upwards_trend:",
                #text=text,
                username='kbpro',
                blocks=blocks,
                thread_ts=None #thread_ts
            )
        else:  
            user_id = user
            username = user
            response = web_client.chat_postMessage(
                channel=channel_id,
                as_user=True,
                user=user_id,
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
    msg = {'question': question, "answer": answer}
    r.lpush('edited', json.dumps(msg).encode('utf-8'))
    logger.info(f"Storing edited answer  in NEO4J - {question} {answer}")

def delete_answer(question, answer):
    ans = {"answer": answer, "question": question}
    r.lpush('deletable_answers', json.dumps(ans).encode('utf-8'))
    sleep(2.5)
    logger.info("We are deleting this answer - {answer}")    

def delete_question(question):
    q = {"question": question}
    r.lpush('deletable_questions', json.dumps(q).encode('utf-8'))
    sleep(2.5)
    logger.info("We are deleting this question - {q}")

def read_question(msg):
    if not msg:
        return 'Empty question sent, sorry'
    answer = {"answer": msg}
    r.lpush('searched_questions', json.dumps(answer).encode('utf-8'))
    sleep(2.5)
    logger.info("Looking for question in daemon -->")

    key = encode(msg)    
    question_key = f'{key}-question'
    question = r.get(question_key)
    if not question:
        return None
    else:
        return question.decode('utf-8')


def read_answers(msg):
    if not msg:
        return [default_answer]
    elif msg == default_answer:
        return [default_answer]    
    answers = []
    r.lpush('multi-answer-questions', msg)
    sleep(5.5)
    key = encode(msg)
    answer_key = f'{key}-answers'
    l = r.llen(f'{key}-answers')

    while(r.llen(f'{key}-answers')!=0):
            item = r.lpop(f'{key}-answers')
            answers.append(item.decode('utf-8'))
    return answers


def read_answer(msg):
    if not msg:
        return default_answer
    elif msg == default_answer:
        return default_answer

    r.lpush('questions', msg)
    key = encode(msg)
    answer_key = f'{key}-answer'
    answer = r.get(answer_key)
 
    if not answer:
        return default_answer
    elif answer == default_answer:
        return default_answer
    else:
        return answer.decode('utf-8')
