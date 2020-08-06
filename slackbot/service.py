#!/usr/bin/env python
import asyncio
import faust
import json
import logging
import os
from utils import read_env, read_approved
from actions import answer_next, submit_edited, make_permanent, make_nonpermanent
from bot import bot
#from kafka import KafkaConsumer

app = faust.App('slackbot-service-ask', broker=read_env('KAFKA_LISTENER'))
approval_topic = app.topic("approve")
editing_topic = app.topic("edit") 
dismissal_topic = app.topic("dismiss")
make_permanent_topic = app.topic("make_permanent")
make_nonpermanent_topic = app.topic("make_nonpermanent")
submit_edited_topic = app.topic("submit_edited")
answers_table = app.Table("answers", default=str)
questions_table = app.Table("questions", default=str)


KAFKA_BROKER = read_env('KAFKA_LISTENER')
logger = logging.getLogger(__name__)

@app.service
class FaustService(faust.Service):
    async def on_start(self) -> None:
        try:
            await bot.run()
        except Exception as e:
            pass
        self.log.info('STARTED')

    async def on_stop(self) -> None:
        self.log.info('STOPPED')


@app.agent(make_nonpermanent_topic)
async def processs_nonpermanent(checkboxes) -> None:
    async for payload in checkboxes:
        logger.info(f"ANOTHER NONPERMANENT CHECKBOX  {payload}")
        make_nonpermanent(payload)


@app.agent(make_permanent_topic)
async def processs_permanent(checkboxes) -> None:
    async for payload in checkboxes:
        logger.info(f"ANOTHER CHECKBOX  {payload}") 
        make_permanent(payload)


@app.agent(submit_edited_topic)
async def processs_submissions(submissions) -> None:
    async for payload in submissions:
        logger.info(f"ANOTHER SUBMISSION {payload}")
        submit_edited(payload)


@app.agent(dismissal_topic)
async def processs_dismissals(dismissals) -> None:
    async for dismissal in dismissals:
        logger.info(f"ANOTHER DISMISSAL {dismissal}") 
        user = dismissal['user']
        channel_id = dismissal['channel']['id']
        message_ts = dismissal['container']['message_ts']
        answer = dismissal['actions'][0]['selected_option']['value'].split('dismiss_')[1]
        answer_next(answer, user, channel_id, None, action='dismiss')


@app.agent(approval_topic)
async def processs_approvals(approvals) -> None:
    async for approval in approvals:  # type: str
        user = approval['user']
        channel_id = approval['channel']['id']
        message_ts = approval['container']['message_ts']
        answer = approval['actions'][0]['selected_option']['value'].split('approve_')[1]
        answer_next(answer, user, channel_id, None, action='approve')


@app.agent(editing_topic) 
async def processs_editings(editings) -> None:
    async for editing in editings:  # type: str
        user = editing['user']
        trigger_id = editing.get('trigger_id', None)
        channel_id = editing['channel']['id']
        message_ts = editing['container']['message_ts']
        answer = editing['actions'][0]['selected_option']['value'].split('edit_')[1]
        answer_next(answer, user, channel_id, trigger_id, action='edit')


@app.timer(2.5)
async def producer():
    pass

def run_producer(msg):
    pass

def main():
    #kw = {
    #    'format': '[%(asctime)s] %(message)s',
    #    'datefmt': '%m/%d/%Y %H:%M:%S',
    #    'level': logging.DEBUG if settings.DEBUG else logging.INFO,
    #    'stream': sys.stdout,
    #}
    #logging.basicConfig(**kw)
    #logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.WARNING)
    app.main()


if __name__=='__main__':
    app.main()
