from datetime import datetime
import faust


class Question(faust.Record, isodates=True):
    question: str
    timestamp: datetime


class Answer(faust.Record, isodates=True):
    question: str
    answer: str
    timestamp: datetime
