# coding=utf8
import os
from slackbot.bot import respond_to
from slackbot.utils import download_file, create_tmp_file, read_answer, store_answered
from slackbot.models import Pending


@respond_to(r'store \<?(.*)\>?')
def store(message, thing):
    """ """
    try:
        p = Pending.read_latest()
        if p:
            p.mark_as_answered()
            store_answered(p.question, thing)
        message.reply(f'Stored answer to question by {p.username} - {thing}')
    except Exception as e:
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
