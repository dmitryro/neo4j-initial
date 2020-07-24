# coding=utf8
import os

from slackbot.bot import respond_to
from slackbot.utils import download_file, create_tmp_file


@respond_to(r'deploy \<?(.*)\>?')
def deploy(message, thing):
    message.reply(f'Creating a pull request for {thing}')


@respond_to('^reply_webapi$')
def deploy_webapi(message):
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
