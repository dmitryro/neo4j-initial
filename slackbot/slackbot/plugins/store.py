# coding=utf8
from datetime import datetime
import logging
from slackbot.bot import respond_to
from slackbot.utils import read_answer, store_answered, encode
from slackbot.models import Pending, Mapping

logger = logging.getLogger(__name__)


@respond_to(r'store \<?(.*)\>?')
def store(message, thing):
    """ """
    try:
        p = Pending.read_latest()
        if p:
            m = Mapping(question_compressed=str(encode(thing)), 
                        answer_compressed=str(encode(p.question)), version=0.01)
            m.save()
            p.mark_as_answered()
            store_answered(p.question, thing)
        message.reply(f'Stored answer to question by {p.username} - {thing}')
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
