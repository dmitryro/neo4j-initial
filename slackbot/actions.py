from datetime import datetime
import logging
from models import Pending, Mapping, Deletable, Permanent, Channel, EncodedMapping
from utils import read_answer, read_answers, store_answer, read_question
from utils import  edit_answer, extend_answer, delete_answer
from utils import decode, encode, respond, read_env
from utils import respond_next, delete_ephemeral, get_uuid


logger = logging.getLogger(__name__)
default_answer = read_env("SLACK_DEFAULT_ANSWER")


def fetch_question(answer):
    question  = read_question(answer)
    return question


def update_store(question, answer, operation='edit'):
    if operation=='store':
        store_answer(question, answer)
    else:
        edit_answer(question, answer)
    return True


def create_mapping(question, original_answer, new_answer):
    logger.info("It's time to check our mappings ...")
    try:
        mapping = Mapping.find_by_answer(original_answer)
        if not mapping:
            mapping = Mapping(question_compressed=str(encode(question)), 
                              answer_compressed=str(encode(new_answer)), version=0.01)
            mapping.save()
            logger.info("Just created a new mapping for {question} - {new_answer}")
        else:
            logger.info("Founc an existing mapping for {question} - {original_answer} - updating ")
            Mapping.update_answer(question, new_answer)
    except Exception as e:
        logger.error(f"Something went wrong when we were trying to create a mapping - {e}")


def auto_slash_command(payload:dict):
    pass


def submit_edited(payload:dict, index:int):
    """ Submite edited answer """
    action_id = payload["view"]["blocks"][1]["accessory"]["action_id"]
    token = payload["token"]
    user = payload["user"]
    message_ts = ""
    user_id = payload["user"]["id"]
    team_id = payload["user"]["team_id"]
    app_id = payload["api_app_id"]
    channel = Channel.find_by_app(app_id, token, team_id, user_id)
    channel_id = channel.channel_id
    Channel.delete_by_app(app_id, token, team_id, user_id)
    original_answer = payload["view"]["blocks"][0]["element"]["initial_value"]
    answer = payload["view"]["state"]["values"]["b-id"]["ml_input"]["value"]
    question = fetch_question(original_answer)
    
    try:
        mapping = EncodedMapping.find_by_answer(encode(original_answer))

        if mapping:
            uuid = mapping.uuid
        else:
            uuid = get_uuid()

        p = Permanent.find_by_action(action_id, token)
        if p:
            create_mapping(question, original_answer, answer)
            update_store(question, answer, operation='edit')
            logger.info(f"Updating or original answer \"{original_answer}\" with \"{answer}\"")
    except Exception as e:
        uuid = get_uuid()
        logger.error("Failed processing permanent {e}")

    EncodedMapping.update_future_answer(uuid, encode(answer))
    answer_next(answer, uuid, user, channel_id, None, message_ts, index, action='confirm')


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
    """ Answer a slack request """
    question = payload['data']['text']#.split(None, 1)[1]
    real_answers = read_answers(question)
    user = payload['data']['user']
    message_ts = payload['data']['ts']
     
    if not real_answers:
        p = Pending(username=f"{user['id']}", real_name=f"{user['id']}", question=question)
        p.save()
        real_answers = [{encode(default_answer):get_uuid()}]
        ephemeral=True
    else:
        ephemeral=False
        mapping = Mapping.find_by_question(question)
        if mapping:
            mapping.compressed_answer = encode(real_answers[0])
            mapping.update()

        else:
            mapping = Mapping(answer_compressed=str(encode(real_answers[0])),
                              question_compressed=str(encode(question)), version=0.01)
            mapping.save()

        p = Pending.latest_by_question(question)
        if not p:
            p = Pending(username=f"{user['id']}", real_name=f"{user['id']}", question=question)
            p.save()
    answers = []

    for answer in real_answers:
        encmapping = EncodedMapping.find_by_answer(encode(answer))
        if not encmapping:
            uuid = get_uuid()
            encmapping = EncodedMapping(question=encode(question), answer=encode(answer), uuid=uuid, message_ts=message_ts)
            encmapping.save()
        answers.append({encode(answer):encmapping.uuid})
    if len(real_answers) == 0:
            uuid = get_uuid()
            encmapping = EncodedMapping(question=encode(question), answer=encode(default_answer), uuid=uuid, message_ts=message_ts)
            encmapping.save()
            answers.append({encode(default_answer):encmapping.uuid})           
    logger.info(f"===============> LET US SEE 1 {payload}")
    respond(payload, text=None, question=question, answers=answers,  ephemeral=ephemeral)
 

def prepare_answers(real_answers, message_ts):
    answers = []
    for answer in real_answers:
        encmapping = EncodedMapping.find_by_answer(encode(answer))
        if not encmapping:
            uuid = get_uuid()
            encmapping = EncodedMapping(answer=encode(answer), uuid=uuid, message_ts=message_ts)
            encmapping.save()
        answers.append({encode(answer):encmapping.uuid})
    return answers

def preview_answer(payload):
    """ Answer a slack request """
    question = payload['data']['text']#.split(None, 1)[1]
    real_answers = read_answers(question)
    user = payload['data']['user']
    message_ts = payload['data']['ts']
    question_compressed = encode(question)
    channel_id = payload['data']['channel']

    p = Pending(username=f"{user}", real_name=f"{user}", question=question)
    p.save()

    if len(real_answers) == 0:
        key = encode(default_answer)
        value = get_uuid()
        ans = {}
        ans[key] = value
        answers =  [ans]
        ephemeral=True
    else:
        ephemeral=False
        mapping = Mapping.find_by_question(question)
        if mapping:
            mapping.compressed_answer = encode(real_answers[0])
            mapping.update()

        else:
            mapping = Mapping(answer_compressed=str(encode(real_answers[0])),
                              question_compressed=str(encode(question)), version=0.01)
            mapping.save()

        p = Pending.latest_by_question(question)

    if len(real_answers):
        answer_compressed = encode(real_answers[0])
        deletable = Deletable(question_compressed=question_compressed, 
                              answer_compressed=answer_compressed,
                              channel_id=channel_id,
                              message_ts=message_ts)
        deletable.save()    
    preview_answer=f'Hi admin! The user <@{user}> just asked' 

    answers = prepare_answers(real_answers, message_ts)
    if len(real_answers) == 0:
            uuid = get_uuid()
            encmapping = EncodedMapping(question=encode(question), answer=encode(default_answer), uuid=uuid, message_ts=message_ts)
            encmapping.save()
            answers.append({encode(default_answer):encmapping.uuid})
    logger.info(f"===============> LET US SEE 2 {payload}")

    if isinstance(user, str):
        payload['data']['user'] = {'id': user, "username": "KBPRO"}

    respond(payload, text=preview_answer, question=question, answers=answers, ephemeral=True)


def make_nonpermanent(payload:dict):
    try:
        action_id=payload["actions"][0]["action_id"]
        token=payload["token"]
        Permanent.delete_by_action(token=token, action_id=action_id)
    except Exception as e:
        logger.error(f"We failed deleting non-permanent item {e}")


def make_permanent(payload:dict):
    p = Permanent(action_id=payload["actions"][0]["action_id"],
                  action_ts=payload["actions"][0]["action_ts"],
                  value=payload["actions"][0]["selected_options"][0]["value"],
                  token=payload["token"])
    p.save()              


def answer_next_with_uuid_and_answer(uuid:str, user:dict, channel_id:str, trigger_id:str, index:int, action='approve'):
    mapping = EncodedMapping.find_by_uuid(uuid)
    message_ts = mapping.message_ts
    future_answer = mapping.future_answer
    EncodedMapping.update_answer(uuid, future_answer) 
    answer_next(decode(future_answer), uuid, user, channel_id, trigger_id, message_ts, index, action=action)


def answer_next_with_uuid(uuid:str, user:dict, channel_id:str, trigger_id:str, index:int, action='approve'):
    mapping = EncodedMapping.find_by_uuid(uuid)
    real_answer = decode(mapping.answer)
    message_ts = mapping.message_ts
    answer_next(real_answer, uuid, user, channel_id, trigger_id, message_ts, index, action=action)
    

def answer_next(answer:str, uuid:str, user:dict, channel_id:str, trigger_id:str, message_ts:str, index:int, action='approve'):
    question = fetch_question(answer)
    answers = []
    if action == 'delete':
        logger.info("fDeleting answer {answer} for question {question}")
        delete_answer(question, answer)
        EncodedMapping.delete_by_answer(encode(answer))
        real_answers = read_answers(question) 
        answers = prepare_answers(real_answers, message_ts)
        logger.info(f"Deleted answer {answer} ... {question} ") 

    p = Pending.latest_by_question(question)
    if not p:
        p = Pending(username=f"{user}", real_name=f"{user}", question=question)
        p.save()    
  
    respond_next(answer, uuid, question, answers, user, channel_id, trigger_id, message_ts, index, action=action)


def store(payload, trim=True):
    """ """
    user = payload['data']['user']
    try:
        if trim:
            answer = payload['data']['text'].split(None, 1)[1]
        else:
            answer = payload['data']['text']

        p = Pending.latest()

        if p:
            update_store(p.question, answer, operation='store')
            p.mark_as_answered()
            msg = f'Stored answer to question by  <@{p.username}>:  {answer}'
        else:
            msg = "I was unable to store a response"
    except Exception as e:
        logger.error(f"Was unable to store the answer {e}")
        msg = f'Was unable to store a response - pending question not found {e}'
    if isinstance(user, str):
        payload['data']['user'] = {'id': user, "username": "KBPRO"}
    respond(payload, text=msg, ephemeral=True)


def store_slash_command(payload:dict):
    logger.info(f"LET US PARSE OUR PAYLOAD {payload}")
    answer = payload['text']
    user_id = payload['user_id']
    channel_id = payload['channel_id']
    username = payload['user_name']
    trigger_id = payload['trigger_id']

    payload['data'] = {'text':answer,
                       'ts': None,
                       'trigger_id': trigger_id,
                       'channel': channel_id, 
                       'user':{'id':user_id, 'username':username}}
    store(payload, trim=False)

def relate(payload):
    """ """
    try:
        logger.info("IDs we got were ")
        msg = f'Marked two questions as related'
    except Exception as e:
        logger.error(f"Was unable to store the answer {e}")
        msg = f'Was unable to store a response - pending question not found {e}'
    respond(payload, text=msg, ephemeral=True)


def edit(payload):
    """ Amend recent answer """
    try:
        ans = payload['data']['text'].split(None, 1)[1]
        mapping = Mapping.find_by_answer(ans)

        if mapping:
            answer = decode(mapping.answer_compressed)
            question = decode(mapping.question_compressed)
            mapping.answer_compressed=encode(ans)
            mapping.update()
        else:
            latest = Pending.latest_answered()
            if not latest:
                question = read_question(ans)
            else:
                question = latest.question

            answer = read_answer(question)
            mapping = Mapping(question_compressed=str(encode(question)),
                              answer_compressed=str(encode(ans)), version=0.01)
            mapping.save()

        edit_answer(question, ans)
        msg = f'Edited previous answer "{answer}" given to question "{question} to become {ans}" '
    except Exception as e:
        logger.error(f"Was unable to amend/edit the answer {e}")
        msg = f'Was unable to amend/edit - mapping not found {e}'

    respond(payload, text=msg, ephemeral=True)


def misc_message(payload):
    """ Need more clarity """
    respond(payload, text=f"MISC - {default_answer}", ephemeral=True)
