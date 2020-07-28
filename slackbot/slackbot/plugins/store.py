# coding=utf8
from datetime import datetime
import logging
from slackbot.bot import respond_to
from slackbot.utils import read_answer, store_answer, read_question
from slackbot.utils import  edit_answer, extend_answer
from slackbot.utils import decode, encode
from slackbot.models import Pending, Mapping

logger = logging.getLogger(__name__)


@respond_to(r'store \<?(.*)\>?')
def store(message, thing):
    """ """
    try:
        p = Pending.latest()
        logger.info(f"=======>> Found pending {p}")

        if p:
            m = Mapping(answer_compressed=str(encode(thing)), 
                        question_compressed=str(encode(p.question)), version=0.01)
            m.save()
            p.mark_as_answered()
            store_answer(p.question, thing)
            message.reply(f'Stored answer to question by {p.username} - {thing}')
    except Exception as e:
        logger.error(f"Was unable to store the answer {e}")
        message.reply(f'Was unable to store a response - pending question not found {e}')



@respond_to(r'extend \<?(.*)\>?')
def extend(message, thing):
    """ Extend recent answer """
    try:
        mapping = Mapping.latest()
        question = decode(mapping.question_compressed)
        answer = decode(mapping.answer_compressed)
        message.reply(f'Extended previous answer "{answer}" given to question "{question}" ')
    except Exception as e:
        logger.error(f"Was unable to extend the answer {e}")
        message.reply(f'Was unable to extend - mapping not found {e}')


@respond_to(r'edit \<?(.*)\>?')
def amend(message, thing):
    """ Amend recent answer """
    try:
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
        message.reply(f'Edited previous answer "{answer}" given to question "{question} to become {thing}" ')
    except Exception as e:
        logger.error(f"Was unable to amend/edit the answer {e}")
        message.reply(f'Was unable to amend/edit - mapping not found {e}')


@respond_to(r'relate \d{1,} \d{1,}')
def relate(message, thing):
    """ """
    try:
        logger.info(f"IDs we got were {thing}")
        message.reply(f'Marked two questions as related')
    except Exception as e:
        logger.error(f"Was unable to store the answer {e}")
        message.reply(f'Was unable to store a response - pending question not found {e}')


@respond_to('^reply_webapi$')
def store_webapi(message):
    """ """
    message.reply_webapi('Creating pull request!', attachments=[{
        'fallback': 'test attachment',
        'fields': [
            {
                'title': 'test table field',
                'value': 'test table value',
                'short': True
            }
        ]
    }])
