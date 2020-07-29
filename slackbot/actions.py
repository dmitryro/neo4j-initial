from datetime import datetime
import logging
from models import Pending, Mapping
from utils import read_answer, store_answer, read_question
from utils import  edit_answer, extend_answer
from utils import decode, encode, respond, read_env

logger = logging.getLogger(__name__)
default_answer = read_env("SLACK_DEFAULT_ANSWER")


def answer(payload):
    """ Anaswer a slack request """

    thing = payload['data']['text'].split(None, 1)[1]
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


def store(payload):
    """ """
    try:
        thing = payload['data']['text'].split(None, 1)[1]
        logger.info(f"WE WILL TRY TO STORE -- {thing} ")
        p = Pending.latest()
        logger.info(f"=======>> Found pending {p}")

        if p:
            m = Mapping(answer_compressed=str(encode(thing)),
                        question_compressed=str(encode(p.question)), version=0.01)
            m.save()
            p.mark_as_answered()
            store_answer(p.question, thing)
            msg = f'Stored answer to question by {p.username} - {thing}'
        else:
            msg = "I was unable to store a response"
    except Exception as e:
        logger.error(f"Was unable to store the answer {e}")
        msg = f'Was unable to store a response - pending question not found {e}'

    respond(msg, payload, ephemeral=True)


def relate(payload):
    """ """
    try:
        logger.info(f"IDs we got were {thing}")
        msg = f'Marked two questions as related'
    except Exception as e:
        logger.error(f"Was unable to store the answer {e}")
        msg = f'Was unable to store a response - pending question not found {e}'

    respond(msg, payload, ephemeral=True)


def edit(payload):
    """ Amend recent answer """
    try:
        thing = payload['data']['text'].split(None, 1)[1]
        mapping = Mapping.latest(thing)
        logger.info(f"WE WILL TRY TO EDIT {thing}")

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

    respond(msg, payload, ephemeral=True)


def misc_message(payload):
    """ Need more clarity """
    respond(default_answer, payload, ephemeral=True)
