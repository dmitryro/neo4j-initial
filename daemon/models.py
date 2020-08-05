from datetime import datetime
import faust


class Question(faust.Record, isodates=True, serializer='json'):
    question: str
    timestamp: datetime


class Answer(faust.Record, isodates=True, serializer='json'):
    question: str
    answer: str
    timestamp: datetime


class Addition(faust.Record, isodates=True, serializer='json'):
    answer: str
    index: int
    text: str
    timestamp: datetime
