# coding=utf8
import logging
import os
from slackbot.bot import respond_to
from slackbot.utils import download_file, create_tmp_file
from slackbot.utils import read_answer, save_pending, read_env
from slackbot.models import Pending 


logger = logging.getLogger(__name__)
default_answer = read_env("SLACK_DEFAULT_ANSWER")

@respond_to(r'answer \<?(.*)\>?')
def answer(message, thing):
    """ Anaswer a slack request """
    answer = read_answer(thing)
    if not answer or answer == default_answer:
        p = Pending(username=message.user['name'], real_name=message.user['real_name'], question=thing)
        p.save()

    message.reply(f'{answer}  ')


@respond_to('^reply_webapi$')
def answer_webapi(message):
    """ """
    message.reply_webapi('Answering!', attachments=[{
        'fallback': 'test attachment',
        'fields': [
            {
                'title': 'test table field',
                'value': 'test table value',
                'short': True
            }
        ]
    }])
