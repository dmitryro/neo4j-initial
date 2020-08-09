#!/usr/bin/env python

import aiotools
import asyncio
import faust
import json
import logging
import os
from threading import Thread
from slack import RTMClient
from slack.errors import SlackApiError
from lex import QuestionDetector
from actions import edit, store, answer, preview_answer, misc_message
from utils import read_env, encode, decode, read_approved
from decorators import daemonize, async_timeout, on_approved, run_async
from singleton import SingletonMeta
import time
from time import sleep
#from kafka import KafkaConsumer


logger = logging.getLogger(__name__)


detect = QuestionDetector()



class Bot(metaclass=SingletonMeta):
    def __init__(self):
        token = read_env("SLACK_TOKEN")
        self._rtm_client = RTMClient(token=token)


    @property
    def rtm_client(self):
        return self._rtm_client


    @staticmethod
    @RTMClient.run_on(event="user_change")
    def process_user_change(**payload):
        pass
 

    @staticmethod
    @RTMClient.run_on(event="user_typing")
    def process_user(**payload):
        pass


    @staticmethod
    @RTMClient.run_on(event='message')
    def process_messages(**payload):
        
        trigger_id = payload.get("trigger_id", None)
        message_type = payload.get("type", None)

        data = payload['data']
        #channel_id = data['channel']
        #thread_ts = data['ts']
        #user = data['user']
      
        if 'text' in data:
            sentence = data['text']#.split(None, 1)[1]

            logger.info(f"OUR LOVELY SENTENCE !!!!! {sentence}")

            if 'store' == data['text'].split(None, 1)[0]:
                logger.info(f"===> CASE 1 - sending store - {sentence}")
                store(payload)
            
            elif 'answer' == data['text'].split(None, 1)[0]: 
                logger.info(f"===> CASE 2 - sending answer - {sentence}")
                preview_answer(payload)

            elif 'edit' == data['text'].split(None, 1)[0]:
                logger.info(f"===> CASE 3 - sending edit - {sentence}")
                edit(payload)
            else:
                logger.info(f"CASE 4.1 ==== {sentence} before the check")
                if detect.IsQuestion(sentence):
                    logger.info(f"===> CASE 4 - sending answer- - {sentence}")
                    preview_answer(payload)
            #else:
            #    logger.info(f"===> CASE 5 - Miscelaneous - sending - {sentence}")
            #    misc_message(payload)


    def consume(self, msg):
        logger.info (f'========== Receive offset {msg.offset}, message: { msg.value }' )


    def listen(self):
        pass
        #while True:
            #consumer = KafkaConsumer('approval', bootstrap_servers=['kafka:9092'])
            #for msg in consumer:
             #   logger.info(f"READ FROM KAFKA ------{msg}")



    def _keepactive(self):
        while True:
            time.sleep(30 * 60)
            self._rtm_client.ping()


    async def run(self):
        self._rtm_client.start()            
            #self._rtm_client.stop()
            #self._rtm_client.start()
        _thread.start_new_thread(self._keepactive, tuple())


bot = Bot()
