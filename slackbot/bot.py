import logging
import os
from slack import RTMClient
from slack.errors import SlackApiError
from lex import QuestionDetector
from actions import edit, store, answer, misc_message

logger = logging.getLogger(__name__)
read_env = lambda property: os.environ.get(property, None)

detect = QuestionDetector()

class Bot(object):
    def __init__(self):
        token = read_env("SLACK_TOKEN")
        self._rtm_client = RTMClient(token=token)

    @staticmethod
    @RTMClient.run_on(event='message')
    def process_messages(**payload):
        data = payload['data']

        if 'text' in data:
            sentence = data['text'].split(None, 1)[1]
            logger.info(f"text was in data {sentence}")

            if 'store' == data['text'].split(None, 1)[0]:
                logger.info("case 1 - sending store")
                store(payload)

            elif 'answer' == data['text'].split(None, 1)[0]: 
                print("sending answer")
                logger.info("case 2 - sending answer")
                answer(payload)

            elif detect.IsQuestion(sentence):
                print("sending answer")
                logger.info("case 3 - sending answer")
                answer(payload)

            elif 'edit' == data['text'].split(None, 1)[0]:
                logger.info("case 4 - sending edit")
                edit(payload)
            else:
                logger.info("case 5 - Miscelaneous message - sending")
                misc_message(payload)

    def _keepactive(self):
        logger.info('keep active thread started')
        while True:
            time.sleep(30 * 60)
            self._rtm_client.ping()


    def run(self):
        self._rtm_client.start()            
        _thread.start_new_thread(self._keepactive, tuple())
        logger.info('connected to slack RTM api')


    def _keepactive(self):
        logger.info('keep active thread started')
        while True:
            time.sleep(30 * 60)
            self._client.ping()
