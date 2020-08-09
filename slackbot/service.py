#!/usr/bin/env python
import asyncio
import faust
import json
import logging
import os
from utils import read_env, read_approved
from actions import answer_next_with_uuid, submit_edited, make_permanent
from actions import record_channel, make_nonpermanent
from bot import bot
from time import sleep
#from kafka import KafkaConsumer

app = faust.App('slackbot-service-ask', broker=read_env('KAFKA_LISTENER'))
approval_topic = app.topic("approve")
record_channel_topic = app.topic("record_channel")
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

@app.agent(submit_edited_topic)
async def processs_submissions(submissions) -> None:
    index = 0
    async for payload in submissions:
        index = index + 1
        submit_edited(payload, index)
    
@app.agent(record_channel_topic)
async def process_record_channel(channels) -> None:
    async for payload in channels:
        record_channel(payload)

@app.agent(make_nonpermanent_topic)
async def processs_nonpermanent(checkboxes) -> None:
    async for payload in checkboxes:
        make_nonpermanent(payload)

@app.agent(make_permanent_topic)
async def processs_permanent(checkboxes) -> None:
    async for payload in checkboxes:
        make_permanent(payload)

@app.agent(submit_edited_topic)
async def processs_submissions(submissions) -> None:
    async for payload in submissions:
        submit_edited(payload)

@app.agent(dismissal_topic)
async def processs_dismissals(dismissals) -> None:
    index = 0
    async for dismissal in dismissals:
        index = index + 1
        user = dismissal['user']
        trigger_id = editing.get('trigger_id', None)
        channel_id = dismissal['channel']['id']
        message_ts = dismissal['container']['message_ts']
        answer = dismissal['actions'][0]['selected_option']['value'].split('dismiss_')[1]
        answer_next_with_uuid(answer, user, channel_id, trigger_id, index, action='dismiss')

@app.agent(approval_topic)
async def processs_approvals(approvals) -> None:
    index = 0
    async for approval in approvals:  # type: str
        index = index + 1
        user = approval['user']
        channel_id = approval['channel']['id']
        message_ts = approval['container']['message_ts']
        answer = approval['actions'][0]['selected_option']['value'].split('approve_')[1]
        answer_next_with_uuid(answer, user, channel_id, None, index, action='approve')
        sleep(5)

@app.agent(editing_topic) 
async def processs_editings(editings) -> None:
    index = 0
    async for editing in editings:  # type: str
        index = index + 1
        user = editing['user']
        trigger_id = editing.get('trigger_id', None)
        channel_id = editing['channel']['id']
        message_ts = editing['container']['message_ts']
        answer = editing['actions'][0]['selected_option']['value'].split('edit_')[1]
        answer_next_with_uuid(answer, user, channel_id, trigger_id, index, action='edit')



def run_producer(msg):
    pass

def main():
    app.main()


if __name__=='__main__':
    app.main()
