import logging
from flask import Flask
from slackify import Slackify, async_task


app = Flask(__name__)
slackify = Slackify(app=app)

logger = logging

@slackify.command
def hello():
    return reply_text('Hello from Slack')


# Change the slash command name to /say_bye instead of the default function name
@slackify.command(name='say_bye')
def bye():
    my_background_job()
    return reply_text('Bye')


@slackify.action("answer_action")
def answer_action():
    """You may ask here, why do we respond to response_url instead of the request itself?
    Well, slack decided you can't respond directly to interaction actions requests.
    So we must use the response_url. If you know why did they decide this please tell
    me. I'm sure they might be a reason but it isn't obvious to me..
    """
    action = json.loads(sl_request.form["payload"])
    logger.info(f"ACTION ======+> HI THERE SEE {action}")
    text_blok = text_block('Super! I do too :thumbsup:')
    blocks = {'blocks': [text_blok]}
    respond(action['response_url'], blocks)
    return OK


@slackify.shortcut('answer_action')
def answer_shortcut():
    action = json.loads(sl_request.form["payload"])
    logger.info(f"SHORTCUT ======+> HI THERE SEE {action}")
    text_blok = text_block('Super! I do too :thumbsup:')
    blocks = {'blocks': [text_blok]}
    respond(action['response_url'], blocks)
    return OK


@async_task
def my_background_job():
    """Non blocking long task"""
    sleep(15)
    return
