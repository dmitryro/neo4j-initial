import faust

class Question(faust.Record):
    slack_id: str
    channel_id: str
    text: str
