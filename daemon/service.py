"""daemin/service.py
This is the async daemon to post into kafka and consume from kafka
"""
import aredis
from aredis import StrictRedis
import asyncio
from datetime import datetime
import faust
from graph import find_answer, add_question, edit_question
import json
import logging
from redis import StrictRedis as RegularStrictRedis
from time import sleep

from models import Answer, Question
from utils import decode, encode, read_env

redis = dict()
redis['host'] = read_env('REDIS_HOST')
redis['port'] = read_env('REDIS_PORT')
redis['db'] = read_env('REDIS_DB')

r = RegularStrictRedis(**redis)
ar = StrictRedis(**redis)
# In case we find no other answer
default_answer = read_env("SLACK_DEFAULT_ANSWER")

app = faust.App('service-ask', broker=read_env('KAFKA_LISTENER'))
answers_table = app.Table('answers', default=str)
questions_table = app.Table('questions', default=str)


logger = logging.getLogger(__name__)

@app.service
class FaustService(faust.Service):

    async def on_start(self) -> None:
        self.log.info('STARTED')

    async def on_stop(self) -> None:
        self.log.info('STOPPED')


@app.agent(value_type=str)
async def str_consumer(stream):
    async for message in stream:
        logger.info(f'Received string: {message!r}')


@app.agent(value_type=str)
async def store_question(stream):
    async for message in stream:
        key = encode(message)
        await ar.set(f'{key}-question', message)

        if key not in questions_table.keys():
            question = Question(question=message, timestamp=datetime.now())
            questions_table[key] = question


@app.agent(value_type=Question)
async def consumer(stream):
    async for message in stream:
        logger.info(f"Will try to find the answer to {message.question}")
        key = encode(message.question)
        answer = find_answer(message.question)

        if not answer:
            answer = answers_table[key]

            if not answer:
               answer = default_answer

            answer = Answer(question=message.question, answer=answer, timestamp=datetime.now())
            answers_table[key] = answer
            answer_key = f'{key}-answer'
            await ar.set(answer_key, answer.answer)
            logger.info(f"=>The answer is {answer.answer} and it's stored under key {answer_key}")         
        else:
            ans = Answer(question=message, answer=answer, timestamp=datetime.now())
            answers_table[key] = ans
            answer_key = f'{key}-answer'
            await ar.set(answer_key, ans.answer)
            logger.info(f"Found answer to {message} and it is {ans.answer}")
    
        logger.info(f'Received question: {message.question!r}')


async def produce_searched_questions():
    while(await ar.llen('searched_questions')!=0):
        item = await ar.lpop('searched_questions')
        d = json.loads(item)
        logger.info(f"Finding question for an answer {d['answer']}")
        answer = d['answer']
        q = find_question(answer)
        await store_question.send(value=q)


async def produce_answered():
    while(await ar.llen('answered')!=0):
        item = await ar.lpop('answered')
        d = json.loads(item)
        logger.info(f"STORING ANSWER {d['answer']} to question {d['question']}")
        q = d['question']
        a = d['answer']
        add_question(**d)
        await store_question.send(value=q)


async def produce_edited():
    logger.info(f"We are about to produce edited answers")

    while(await ar.llen('edited')!=0):
        item = await ar.lpop('edited')
        d = json.loads(item)
        q = d['question']
        edit_question(**d)
        logger.info(f"EDITING ANSWER - SETTING the answer to question {d['question']} to be {d['answer']}")
        logger.info(f"Updated question {d['question']}:{d['answer']}")
        await store_question.send(value=q)


async def produce_extended():
    logger.info(f"We are about to produce extended answers")

    while(await ar.llen('edited')!=0):
        item = await ar.lpop('extended')
        d = json.loads(item)
        logger.info(f"EXTENDING ANSWER {d['answer']} to question {d['question']} with {d['extension']}")


async def produce_questions():
    questions = []

    while(await ar.llen('questions')!=0):
        item = await ar.lpop('questions')
        questions.append(str(item.decode('utf-8')))

    logger.info(f"New questions we're processing so far {questions}")

    for q in questions:
        logger.info(f"Some question to process {q}")
        #store it in the table
        await store_question.send(value=q)
        key = encode(q)
        answer = find_answer(q)
        if answer:
            question = Question(question=q, timestamp=datetime.now())
            await consumer.send(value=question)
            logger.info(f"Found anwer for {q} - and it is - {answer}")
        else:
            answer = answers_table[key]
            question = questions_table[key]
            if not question:
                question = Question(question=q, timestamp=datetime.now())
                await consumer.send(value=question)

        logger.info(f"Answer so far ... {answer}")


@app.timer(2.5)
async def producer():
    await produce_questions()
    await produce_answered()
    await produce_edited()
    await produce_extended()
    await produce_searched_questions()


def run_producer(msg):
    r.lpush('questions', msg)
    logger.info("Processing answer")
    sleep(5)
    key = encode(msg)
    answer_key = f'{key}-answer'
    answer = r.get(answer_key).decode('utf-8')
    return answer


if __name__ == '__main__':
    app.main()
