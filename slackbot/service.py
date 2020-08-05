#!/usr/bin/env python
import asyncio
import faust
import json
import logging
import os
from utils import read_env, read_approved
from actions import answer_next
from bot import bot
#from kafka import KafkaConsumer

app = faust.App('slackbot-service-ask', broker=read_env('KAFKA_LISTENER'))
approval_topic = app.topic("approve")
editing_topic = app.topic("edit") 
dismissal_topic = app.topic("dismiss")
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


@app.agent(dismissal_topic)
async def processs_dismissals(dismissals) -> None:
    logger.info("HEY! USER DISMISSED SOMETHING!!!!!!")
    async for dismissal in dismissals: 
        user = dismissal['user']
        channel_id = dismissal['channel']['id']
        answer = dismissal['actions'][0]['selected_option']['value'].split('dismiss_')[1]
        answer_next(answer, user, channel_id, action='dismiss')


@app.agent(approval_topic)
async def processs_approvals(approvals) -> None:
    logger.info("HEY! USER APPROVED SOMETHING!!!!!!")
    async for approval in approvals:  # type: str
        user = approval['user']
        channel_id = approval['channel']['id']
        answer = approval['actions'][0]['selected_option']['value'].split('approve_')[1]
        answer_next(answer, user, channel_id, action='approve')


@app.agent(editing_topic) 
async def processs_editings(editings) -> None:
    logger.info("HEY! USER IS EDITING SOMETHING!!!!!!")
    async for editing in editings:  # type: str
        user = editing['user']
        channel_id = editing['channel']['id']
        answer = editing['actions'][0]['selected_option']['value'].split('edit_')[1]
        answer_next(answer, user, channel_id, action='edit')


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
