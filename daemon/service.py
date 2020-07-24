"""examples/service.py
This examples starts a separate :pypi:`mode` service with the app.
If you want the service instance to be generally available
you may create a subclass of app, to define a new app.myservice attribute:
.. sourcecode:: python
    class App(faust.App):
        myservice: MyService
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.myservice = self.service(
                MyService(loop=self.loop, beacon=self.beacon),
            )
    app = App('service-example')
"""
import aredis
from aredis import StrictRedis
import asyncio
from datetime import datetime
import faust
from graph import find_answer
import logging
from redis import StrictRedis as RegularStrictRedis
from time import sleep

from models import Answer, Question
from utils import decode, encode

r = RegularStrictRedis(host='redis', port=6379, db=0)
ar = StrictRedis(host='redis', port=6379, db=0)
r.set('question', 'hello world')


app = faust.App('service-ask', broker='kafka://kafka:9092')
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
        if key not in questions_table.keys():
            question = Question(question=message, timestamp=datetime.now())
            questions_table[key] = question
            await ar.set(f'{key}-question', question.question)


@app.agent(value_type=Question)
async def consumer(stream):
    async for message in stream:
        logger.info(f"Will try tofind the answer to {message.question}")
        key = encode(message.question)
        answer = answers_table[key]


        if not answer:
            answer = find_answer(message.question)
            if not answer:
               'some initial answer'

            answer = Answer(question=message.question, answer=answer, timestamp=datetime.now())
            answers_table[key] = answer
            answer_key = f'{key}-answer'
            await ar.set(answer_key, answer.answer)
            logger.info(f"=>The answer is {answer.answer} and it's stored under key {answer_key}")         
        else:
            logger.info(f"Found answer to {answer.question} and it is {answer.answer}")
    
        logger.info(f'Received question: {message.question!r}')


@app.timer(2.0)
async def producer():
    questions = []

    while(await ar.llen('questions')!=0):
        item = await ar.lpop('questions')
        questions.append(str(item.decode('utf-8')))

    print(f"Questions so far {questions}")
    logger.info(f"Questions so far {questions}")

    for q in questions:
        logger.info(f"Some question to process {q}")
        #store it in the table
        await store_question.send(value=q)   
        key = encode(q) 
        answer = answers_table[key]
        logger.info(f"ANSWER SO FAR {answer}")       
        if answer:
            print(f"Found anwer for {question.question} - and it is - {answer}")
            logger.info(f"Found anwer for {question.question} - and it is - {answer}")
        else:
            question = questions_table[key]
            if not question:
                question = Question(question=q, timestamp=datetime.now())
                logger.info(f"ABOUT TO SEND QUESTION - WAIT {question.question}") 
                print(f"Didn't find anwer for {question.question} - requesting")
                await consumer.send(value=question)

    ## -- this is old 
    #if question:
    #    await consumer.send(value=question)
    #else:
    
    #print("About to send ...")
    #await consumer.send(value=question)
    

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
