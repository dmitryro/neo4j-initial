#!/usr/bin/env python
import asyncio
import faust
import json
import logging
import os
from utils import read_env, read_approved
from actions import answer_approved
from bot import bot
#from kafka import KafkaConsumer

app = faust.App('slackbot-service-ask', broker=read_env('KAFKA_LISTENER'))
approval_topic = app.topic('approval')
answers_table = app.Table('answers', default=str)
questions_table = app.Table('questions', default=str)


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


@app.agent(approval_topic)
async def processs_approvals(approvals) -> None:
    async for approval in approvals:  # type: str
        user = approval['user']
        channel_id = approval['channel']['id']
        answer = approval['actions'][0]['selected_option']['value'].split('approve_')[1]
        answer_approved(answer, user, channel_id)
        logger.info(f"IN SLACKBOT - PROCESSING APPROVAL : {answer} {channel_id} {user}...")


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
