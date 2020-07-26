# coding=utf8
import os
from slackbot.bot import respond_to
from slackbot.utils import download_file, create_tmp_file, read_answer


@respond_to(r'ship \<?(.*)\>?')
def ship(message, thing):
    """ """
    message.reply(f'shipping {thing}')



@respond_to('^reply_webapi$')
def ship_webapi(message):
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
