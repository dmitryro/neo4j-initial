from datetime import datetime
import faust


class Question(faust.Record, isodates=True):
    question: str
    timestamp: datetime


class Answer(faust.Record, isodates=True):
    question: str
    answer: str
    timestamp: datetime


class Addition(faust.Record, isodates=True):
    answer: str
    index: int
    text: str
    timestamp: datetime
