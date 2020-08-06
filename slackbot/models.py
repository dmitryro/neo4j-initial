from datetime import datetime
import faust
import logging
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from utils import obtain_session, encode
from session import SessionManager

session = SessionManager() 

logger = logging.getLogger(__name__)

Base = declarative_base()


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


class Permanent(Base):
    id = Column(Integer, primary_key=True)
    token = Column(String(250), unique=False)
    value = Column(String(250), unique=False)
    action_ts = Column(String(230), unique=False)
    action_id = Column(String(230), unique=False)
    date_added = Column(DateTime(timezone=True),
                                 server_default=func.now(),
                                 nullable=True,
                                 default=None)

    __tablename__ = "permanent"

    def __init__(self, token=None,
                       action_ts=None,
                       value=None,
                       action_id=None):
        self.action_id = action_id
        self.action_ts = action_ts
        self.value = value
        self.token = token
        self.date_added = func.now()    

    def save(self):
        """ Save pending """
        s = session.obtain_session()
        s.add(self)
        s.commit()
 
    def delete(self):
        """ Delete pending - no longer used """
        s = session.obtain_session()
        s.delete(self)
        s.commit()
 
    @staticmethod
    def find_by_action(action_id, token):
        """ Read latest mapping """
        s = session.obtain_session()
        m = s.query(Permanent).filter(and_(Permanent.action_id==action_id,
                                           Permanent.token==token)).order_by(desc('date_added')).first()
        s.commit()
        return m


    @staticmethod
    def delete_by_action(action_id, token):
        """ Delete by action id and token  """
        s = session.obtain_session()
        m = s.query(Permanent).filter(and_(Permanent.action_id==action_id,
                                           Permanent.token==token)).order_by(desc('date_added')).first()
        
        s.delete(m)
        s.commit()


class Deletable(Base):
    id = Column(Integer, primary_key=True)
    message_ts = Column(String(230), unique=False)
    answer_compressed = Column(String(230), unique=False)
    question_compressed = Column(String(230), unique=False)
    channel_id =  Column(String(230), unique=False)
    date_addedd = Column(DateTime(timezone=True),
                                  server_default=func.now(),
                                  nullable=True,
                                  default=None)    


    __tablename__ = "deletable"
    
    def __init__(self, channel_id=None,
                       message_ts=None,
                       answer_compressed=None,
                       question_compressed=None):
        self.answer_compressed = answer_compressed
        self.question_compressed = question_compressed
        self.message_ts = message_ts
        self.channel_id = channel_id
        self.date_added = func.now()

    def save(self):
        """ Save pending """
        s = obtain_session()
        s.add(self)
        s.commit()

    def delete(self):
        """ Delete pending - no longer used """
        s = obtain_session()
        s.delete(self)
        s.commit()
        s.flush()

    @staticmethod
    def latest_by_answer(answer):
        """ Read latest mapping """
        s = obtain_session()
        m = s.query(Deletable).filter(Deletable.answer_compressed==encode(answer)).first()
        return m

    @staticmethod
    def latest_by_question(question):
        """ Read latest mapping """
        s = obtain_session()
        m = s.query(Deletable).filter(Deletable.question_compressed==encode(question)).first()
        return m


class Mapping(Base):
    id = Column(Integer, primary_key=True)
    question_compressed = Column(String(230), unique=False)
    answer_compressed = Column(String(230), unique=False)
    date_modified = Column(DateTime(timezone=True),
                                    server_default=func.now(),
                                    nullable=True,
                                    default=None)    
    version = Column(Float(), unique=False)

    __tablename__ = "mappings"

    def __init__(self, question_compressed=None, 
                       answer_compressed=None, 
                       date_modified=func.now(),
                       version=0.01):
        self.question_compressed = question_compressed
        self.answer_compressed = answer_compressed
        self.date_modified = date_modified
        self.version = version

    def save(self):
        """ Save pending """
        s = obtain_session()
        s.add(self)
        s.commit()

    def delete(self):
        """ Delete pending - no longer used """
        s = obtain_session()
        s.delete(self)
        s.commit()
        s.flush()


    def update(self):
        """ Mark as answered """
        s = obtain_session()
        self.date_modified = func.now()
        query = s.query(Mapping).filter(and_(Mapping.id==self.id,
                                             Mapping.question_compressed==self.question_compressed))
        query.update({"date_modified": func.now(), "answer_compressed": self.answer_compressed}, synchronize_session=False)
        s.commit()


    @staticmethod
    def latest():
        """ Read latest mapping """
        s = obtain_session()
        q = s.query(Mapping).order_by(desc('date_modified')).first()
        return q


    @staticmethod
    def latest_by_question(question):
        """ Read latest mapping """
        s = obtain_session()
        m = s.query(Mapping).filter(Mapping.question_compressed==encode(question)).order_by(desc('date_modified')).first()
        return m


    @staticmethod
    def latest(answer):
        """ Read latest mapping """
        s = obtain_session()
        q = s.query(Mapping).filter(Mapping.answer_compressed==encode(answer)).order_by(desc('date_modified')).first()
        return q


    @staticmethod
    def find(self, id):
        """ Read latest unanswered """
        s = obtain_session()
        m = s.query(Mapping).get(id)
        return m

class Pending(Base):
    """ The user record to save in Postgres """

    id = Column(Integer, primary_key=True)
    username = Column(String(256), unique=False)
    real_name = Column(String(256), unique=False)
    question = Column(String(2564), unique=False)
    date_asked = Column(DateTime(timezone=True),
                                  server_default=func.now())
    date_answered = Column(DateTime(timezone=True),
                                    server_default=func.now(),
                                    nullable=True,
                                    default=None)
    is_approved = Column(Boolean(), default=False)

    __tablename__ = "pending"

    def __init__(self, username=None, real_name=None, question=None):
        self.username = username
        self.question = question
        self.real_name = real_name
        self.date_asked = func.now()
        self.is_approved = False

    def save(self):
        """ Save pending """
        s = obtain_session()
        s.add(self)
        s.commit()
    

    @staticmethod
    def latest_answered():
        """ Read latest answered """
        s = obtain_session()
        q = s.query(Pending).filter(Pending.date_answered!=None).order_by(desc('date_asked')).first()
        return q
    

    @staticmethod
    def latest():
        """ Read latest unanswered """
        s = obtain_session()
        q = s.query(Pending).filter(Pending.date_answered==None).order_by(desc('date_asked')).first() 
        return q


    @staticmethod
    def latest_by_question(question):
        """ Read latest mapping """
        s = obtain_session()
        q = s.query(Pending).filter(Pending.question==question).order_by(desc('date_asked')).first()
        return q


    def mark_as_answered(self):
        """ Mark as answered """
        s = obtain_session()
        self.date_answered = func.now()
        query = s.query(Pending).filter(and_(Pending.id == self.id, 
                                             Pending.username == self.username, 
                                             Pending.date_answered == None))
        query.update({"date_answered": func.now(), "is_approved": True}, synchronize_session=False)
        s.commit()


    def delete(self):
        """ Delete pending - no longer used """
        s = obtain_session()
        s.delete(self)
        s.commit()
        s.flush() 
