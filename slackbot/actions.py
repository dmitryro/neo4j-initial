from datetime import datetime
import logging
from models import Pending, Mapping, Deletable, Permanent, Channel
from utils import read_answer, store_answer, read_question
from utils import  edit_answer, extend_answer
from utils import decode, encode, respond, read_env
from utils import respond_next, delete_ephemeral


logger = logging.getLogger(__name__)
default_answer = read_env("SLACK_DEFAULT_ANSWER")


def fetch_question(answer):
    try:
        mapping = Mapping.latest(answer)
        question = decode(mapping.question_compressed)
    except Exception as e:
        logger.error(f"--> Something went wrong in answer processing, no mapping found -  {e}")
        question  = read_question(answer)
        m = Mapping(answer_compressed=str(encode(answer)),
                    question_compressed=str(encode(question)), version=0.01)
    return question


def update_store(question, answer):

    m = Mapping.latest_by_question(question)
    if m:
        logger.info("Mapping found - updating naswer to be {answer}")
        Mapping.update_answer(question, answer)
    else:
        logger.info("Mapping not found - creating a new one with aswer \"{answer}\" and \"{question}\"")
        m = Mapping(answer_compressed=str(encode(answer)),
                    question_compressed=str(encode(question)), version=0.01)                
        m.save()
    store_answer(question, answer)
    return True


def submit_edited(payload:dict):
    """ Submite edited answer """
    action_id = payload["view"]["blocks"][1]["accessory"]["action_id"]
    token = payload["token"]
    user = payload["user"]
    user_id = payload["user"]["id"]
    team_id = payload["user"]["team_id"]
    app_id = payload["api_app_id"]
    channel = Channel.find_by_app(app_id, token, team_id, user_id)
    channel_id = channel.channel_id
    Channel.delete_by_app(app_id, token, team_id, user_id)
    logger.info(f"WE ARE DONE EDITING {channel_id}")
    original_answer = payload["view"]["blocks"][0]["element"]["initial_value"]
    answer = payload["view"]["state"]["values"]["b-id"]["ml_input"]["value"]
    question = fetch_question(original_answer)

    try:
        p = Permanent.find_by_action(action_id, token)
        if p:
            update_store(question, answer)
            logger.info(f"We are updating or original answer \"{original_answer}\" with \"{answer}\"")
    except Exception as e:
        logger.error("Failed processing permanent {e}")
    answer_next(encode(answer), user, channel_id, None, action='approve')


def record_channel(payload:dict):
    app_id = payload["api_app_id"]
    token = payload["token"]
    channel_id = payload["channel"]["id"]
    team_id = payload["user"]["team_id"]
    user_id = payload["user"]["id"]

    c = Channel(app_id=app_id,
                token=token,
                channel_id=channel_id,
                team_id=team_id,
                user_id=user_id)
    c.save()
    logger.info(f"Saved channel information - {channel_id}")


def answer(payload):
    """ Anaswer a slack request """
    thing = payload['data']['text']#.split(None, 1)[1]
    answer = read_answer(thing)
    user = payload['data']['user']

    if not answer:
        p = Pending(username=f"{user}", real_name=f"{user}", question=thing)
        p.save()
        answer = default_answer
        ephemeral=True
    else:
        ephemeral=False
        mapping = Mapping.latest_by_question(thing)
        if mapping:
            mapping.compressed_answer = encode(answer)
            mapping.update()

        else:
            mapping = Mapping(answer_compressed=str(encode(answer)),
                              question_compressed=str(encode(thing)), version=0.01)
            mapping.save()

        p = Pending.latest_by_question(thing)
        if not p:
            p = Pending(username=user, real_name=user, question=thing)
            p.save()
    
    respond(answer, payload, ephemeral=ephemeral)


def preview_answer(payload):
    """ Anaswer a slack request """
    thing = payload['data']['text']#.split(None, 1)[1]
    answer = read_answer(thing)
    user = payload['data']['user']
    message_ts = payload['data']['ts']
    question_compressed = encode(thing)
    channel_id = payload['data']['channel']
    
    if not answer:
        p = Pending(username=f"{user}", real_name=f"{user}", question=thing)
        p.save()
        answer = default_answer
        ephemeral=True
    else:
        ephemeral=False
        mapping = Mapping.latest_by_question(thing)
        if mapping:
            mapping.compressed_answer = encode(answer)
            mapping.update()

        else:
            mapping = Mapping(answer_compressed=str(encode(answer)),
                              question_compressed=str(encode(thing)), version=0.01)
            mapping.save()

        p = Pending.latest_by_question(thing)
        if not p:
            p = Pending(username=user, real_name=user, question=thing)
            p.save()
    answer_compressed = encode(answer)
    deletable = Deletable(question_compressed=question_compressed, 
                          answer_compressed=answer_compressed,
                          channel_id=channel_id,
                          message_ts=message_ts)
    deletable.save()    
    preview_answer=f'Hi admin! The user <@{user}> just asked' # "{thing}" and the answer I\'m suggesting is "{answer}" - please approve or dismiss!'   
    respond(payload, text=preview_answer, question=thing, answer=answer, ephemeral=True)


def make_nonpermanent(payload:dict):
    try:
        action_id=payload["actions"][0]["action_id"]
        token=payload["token"]
        Permanent.delete_by_action(token=token, action_id=action_id)
        logger.info(f"WE ARE MAKING IT NONPERMANENT ")
    except Exception as e:
        logger.error(f"We failed deleting non-permanent item {e}")


def make_permanent(payload:dict):
    p = Permanent(action_id=payload["actions"][0]["action_id"],
                  action_ts=payload["actions"][0]["action_ts"],
                  value=payload["actions"][0]["selected_options"][0]["value"],
                  token=payload["token"])
    p.save()              


def answer_next(answer:str, user:dict, channel_id:str, trigger_id, action='approve'):
    question = fetch_question(decode(answer))
    respond_next(decode(answer), question, user, channel_id, trigger_id, action=action)


def update_store(question, answer):
    m = Mapping.latest_by_question(question)
    if m:
        Mapping.update_answer(question, answer)
    else:
        m = Mapping(answer_compressed=str(encode(answer)),
                    question_compressed=str(encode(question)), version=0.01)
        m.save()
    store_answer(question, answer)
    return True


def store(payload):
    """ """
    try:
        thing = payload['data']['text'].split(None, 1)[1]
        p = Pending.latest()

        if p:
            update_store(p.question, thing)
            p.mark_as_answered()
            msg = f'Stored answer to question by  <@{p.username}>:  {thing}'
        else:
            msg = "I was unable to store a response"
    except Exception as e:
        logger.error(f"Was unable to store the answer {e}")
        msg = f'Was unable to store a response - pending question not found {e}'

    respond(payload, text=msg, ephemeral=True)


def relate(payload):
    """ """
    try:
        logger.info(f"IDs we got were {thing}")
        msg = f'Marked two questions as related'
    except Exception as e:
        logger.error(f"Was unable to store the answer {e}")
        msg = f'Was unable to store a response - pending question not found {e}'

    respond(payload, text=msg, ephemeral=True)


def edit(payload):
    """ Amend recent answer """
    try:
        thing = payload['data']['text'].split(None, 1)[1]
        mapping = Mapping.latest(thing)

        if mapping:
            answer = decode(mapping.answer_compressed)
            question = decode(mapping.question_compressed)
            mapping.answer_compressed=encode(thing)
            mapping.update()
        else:
            latest = Pending.latest_answered()
            if not latest:
                question = read_question(thing)
            else:
                question = latest.question

            answer = read_answer(question)
            mapping = Mapping(question_compressed=str(encode(question)),
                              answer_compressed=str(encode(thing)), version=0.01)
            mapping.save()

        edit_answer(question, thing)
        msg = f'Edited previous answer "{answer}" given to question "{question} to become {thing}" '
    except Exception as e:
        logger.error(f"Was unable to amend/edit the answer {e}")
        msg = f'Was unable to amend/edit - mapping not found {e}'

    respond(payload, text=msg, ephemeral=True)


def misc_message(payload):
    """ Need more clarity """
    respond(payload, text=f"MISC - {default_answer}", ephemeral=True)
