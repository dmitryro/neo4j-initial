#!/usr/bin/env python
import asyncio
import faust
import json
import logging
import os
from utils import read_env, read_approved
from actions import answer_next_with_uuid, submit_edited, make_permanent
from actions import answer_next_with_uuid_and_answer
from actions import record_channel, make_nonpermanent
from actions import auto_slash_command, store_slash_command
from actions import pr_slash_command, qa_slash_command, jira_slash_command
from bot import bot
from time import sleep
#from kafka import KafkaConsumer

app = faust.App('slackbot-service-ask', broker=read_env('KAFKA_LISTENER'))
approval_topic = app.topic("approve")
record_channel_topic = app.topic("record_channel")
editing_topic = app.topic("edit")
dismissal_topic = app.topic("dismiss")
delete_topic = app.topic("delete")
make_permanent_topic = app.topic("make_permanent")
make_nonpermanent_topic = app.topic("make_nonpermanent")
store_topic = app.topic("store")
auto_topic =  app.topic("auto")
jira_topic = app.topic("jira")
pr_topic = app.topic("pr")
qa_topic = app.topic("qa")
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
        submit_edited(payload, index)
        index = index + 1


@app.agent(store_topic)
async def process_store_channel(stores) -> None:
    async for payload in stores:
        logger.info(f"===========+>WE GOT OUR VALUES - ROUTING IT {payload}")
        store_slash_command(payload)


@app.agent(auto_topic)
async def process_auto_channel(autos) -> None:
    async for payload in autos:
        auto_slash_command(payload) 


@app.agent(jira_topic)
async def process_jira_channel(jiras) -> None:
    async for payload in jiras:
        jira_slash_command(payload)


@app.agent(qa_topic)
async def process_qa_channel(qas) -> None:
    async for payload in qas:
        qa_slash_command(payload)


@app.agent(pr_topic)
async def process_pr_channel(prs) -> None:
    async for payload in prs:
        pr_slash_command(payload)


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
    index = 0
    async for payload in submissions:
        submit_edited(payload, index)
        index = index + 1 


@app.agent(dismissal_topic)
async def processs_dismissals(dismissals) -> None:
    index = 0
    async for dismissal in dismissals:
        user = dismissal['user']
        trigger_id = dismissal.get('trigger_id', None)
        channel_id = dismissal['channel']['id']
        message_ts = dismissal['container']['message_ts']
        answer = dismissal['actions'][0]['selected_option']['value'].split('dismiss_')[1]
        answer_next_with_uuid(answer, user, channel_id, trigger_id, index, action='dismiss')
        index = index + 1 
      
@app.agent(approval_topic)
async def processs_approvals(approvals) -> None:
    index = 0
    async for approval in approvals:  # type: str
        user = approval['user']
        channel_id = approval['channel']['id']
        message_ts = approval['container']['message_ts']
        if approval['actions'][0].get('selected_option', None):
            uuid = approval['actions'][0]['selected_option']['value'].split('approve_')[1]
            answer_next_with_uuid(uuid, user, channel_id, None, index, action='approve')
        else:
            uuid = approval['actions'][0]['value'].split('approve_')[1] 
            answer_next_with_uuid_and_answer(uuid, user, channel_id, None, index, action='approve')
        index = index + 1 
        sleep(3.5)

@app.agent(editing_topic) 
async def processs_editings(editings) -> None:
    index = 0
    async for editing in editings:  # type: str
        user = editing['user']
        trigger_id = editing.get('trigger_id', None)
        channel_id = editing['channel']['id']
        message_ts = editing['container']['message_ts']
        answer = editing['actions'][0]['selected_option']['value'].split('edit_')[1]
        answer_next_with_uuid(answer, user, channel_id, trigger_id, index, action='edit')
        index = index + 1 

@app.agent(delete_topic)
async def processs_deleted(deleted) -> None:
    index = 0
    async for delete in deleted:
        user = delete['user']
        trigger_id = delete.get('trigger_id', None)
        channel_id = delete['channel']['id']
        message_ts = delete['container']['message_ts']
        answer = delete['actions'][0]['selected_option']['value'].split('delete_')[1]
        answer_next_with_uuid(answer, user, channel_id, trigger_id, index, action='delete')
        index = index + 1

def run_producer(msg):
    pass

def main():
    app.main()


if __name__=='__main__':
    app.main()
