import faust
from slackbot.models.question import Question

app = faust.App('ship-app', broker=read_env('KAFKA_LISTENER'))
ship_topic = app.topic('ship-topic', value_type=Question)


@app.agent(ship_topic)
async def process_answers(questions):
    answeres = []

    async for question in questions:
        answers.append("ANSWERED {question.text}")
    ship_topic.send(value=answers)
