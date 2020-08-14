from datetime import datetime
import logging
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

from utils import obtain_session, encode, get_uuid
from session import SessionManager

session = SessionManager() 

logger = logging.getLogger(__name__)

Base = declarative_base()

class Config(Base):
    id = Column(Integer, primary_key=True)
    is_automatic = Column(Boolean(), default=False)
    date_updated = Column(DateTime(timezone=True),
                                   server_default=func.now(),
                                   nullable=True,
                                   default=None)
    email = Column(String(500), unique=False)
    session_id = Column(String(500), unique=False)

    __tablename__ = "config"

    def __init__(self, is_automatic=False,
                       email=None,
                       session_id=None,
                       date_updated=func.now()):
        self.is_automatic = is_automatic
        self.date_updated = date_updated
        self.session_id = session_id
        self.email = email

    def save(self):
        """ Save encodedmapping """
        s = session.obtain_session()
        s.add(self)
        s.commit()


    def on_off(self, onoff):
        """ Mark on or off """
        s = session.obtain_session()
        self.date_answered = func.now()
        query = s.query(Config).filter(Config.id == self.id)
        query.update({"is_automatic": onoff}, synchronize_session=False)
        s.commit()


    @staticmethod
    def automatic(on=False):
        """ Mark as answered """
        s = session.obtain_session()
        query = s.query(Config).filter(Config.id == 1)
        if not query:
            config = Config(is_automatic=False, email='info@gmail.com', session_id = get_uuid())
            config.save()
        query.update({"is_automatic": on}, synchronize_session=False)
        s.commit()

    @staticmethod
    def find_by_id(id):
        """ Read latest mapping """
        s = session.obtain_session()
        m = s.query(Config).filter(Config.id==id).first()
        s.commit()
        return m

    def delete(self):
        """ Delete config - no longer used """
        s = obtain_session()
        s.delete(self)
        s.commit()
        s.flush()

class EncodedMapping(Base):
    id = Column(Integer, primary_key=True)
    question = Column(String(500), unique=False)
    answer = Column(String(500), unique=False)
    future_answer = Column(String(1500), unique=False)
    message_ts = Column(String(230), unique=False)
    uuid = Column(String(230), unique=False)
    date_posted = Column(DateTime(timezone=True),
                                 server_default=func.now(),
                                 nullable=True,
                                 default=None)

    __tablename__ = "encodedmapping"    
 
    def __init__(self, question=None,
                 answer=None,
                 uuid=None, message_ts=None):
         self.question = question
         self.answer = answer
         self.uuid = uuid
         self.message_ts = message_ts
         self.date_posted = func.now()
     

    def save(self):
        """ Save encodedmapping """
        s = session.obtain_session()
        s.add(self)
        s.commit()


    def delete(self):
        """ Delete pending - no longer used """
        s = session.obtain_session()
        s.delete(self)
        s.commit()    


    @staticmethod
    def delete_by_uuid(uuid):
        """ Delete by uuid  """
        s = session.obtain_session()
        m = s.query(EncodedMapping).filter(EncodedMapping.uuid==uuid).first()
        s.delete(m)
        s.commit()


    @staticmethod
    def find_by_uuid(uuid):
        """ Read latest mapping """
        s = session.obtain_session()
        m = s.query(EncodedMapping).filter(EncodedMapping.uuid==uuid).first()
        s.commit()
        return m

    @staticmethod
    def update_answer(uuid, answer):
        """ Mark as answered """
        s = session.obtain_session()
        query = s.query(EncodedMapping).filter(EncodedMapping.uuid == uuid)
        query.update({"answer": answer}, synchronize_session=False)
        s.commit()

    @staticmethod
    def update_future_answer(uuid, answer):
        """ Mark as answered """
        s = session.obtain_session()
        query = s.query(EncodedMapping).filter(EncodedMapping.uuid == uuid)
        query.update({"future_answer": answer}, synchronize_session=False)
        s.commit()

    @staticmethod
    def delete_by_answer(answer):
        """ Read latest mapping """
        s = session.obtain_session()
        m = s.query(EncodedMapping).filter(EncodedMapping.answer==answer).first()
        s.delete(m)
        s.commit()


    @staticmethod
    def find_by_answer(answer):
        """ Read latest mapping """
        s = session.obtain_session()
        m = s.query(EncodedMapping).filter(EncodedMapping.answer==answer).first()
        s.commit()
        return m

    @staticmethod
    def delete_by_question(question):
        """ Read latest mapping """
        s = session.obtain_session()
        m = s.query(EncodedMapping).filter(EncodedMapping.question==question).first()
        s.delete(m)
        s.commit()

    @staticmethod
    def find_by_question(question):
        """ Read latest mapping """
        s = session.obtain_session()
        m = s.query(EncodedMapping).filter(EncodedMapping.question==question).first()
        s.commit()
        return m

    @staticmethod
    def update_by_question(question, answer):
        """ Mark as answered """
        s = session.obtain_session()
        query = s.query(EncodedMapping).filter(EncodedMapping.question == question)
        query.update({"answer": answer}, synchronize_session=False)
        s.commit()

class Question(Base):
    id = Column(Integer, primary_key=True)
    question = Column(String(250), unique=False)
    question_ts = Column(String(250), unique=False)
    channel_id = Column(String(230), unique=False)
    date_posted = Column(DateTime(timezone=True),
                                 server_default=func.now(),
                                 nullable=True,
                                 default=None)
    is_approved = Column(Boolean(), default=False)

    __tablename__ = "question"

    def __init__(self, question=None,
                       question_ts=None,
                       channel_id=None,
                       is_approved=False):
        self.channel_id = channel_id
        self.question_ts = question_ts
        self.question = question
        self.date_posted = func.now()
        self.is_approved = is_approved

    def save(self):
        """ Save pending """
        s = session.obtain_session()
        s.add(self)
        s.commit()

class Answer(Base):
    """ Answer """
    id = Column(Integer, primary_key=True, autoincrement=True)
    answer = Column(String(10200), unique=False)
    answer_ts = Column(String(256), unique=False)
    question_id = Column(Integer, ForeignKey("question.id"), unique=False, nullable=False)
    date_posted = Column(DateTime(timezone=True),
                                 server_default=func.now(),
                                 nullable=True,
                                 default=None)
    is_dismissed = Column(Boolean(), default=False)

    __tablename__ = "answer"

    def __init__(self, question_id=None,
                       answer=None,
                       answer_ts=None,
                       is_dismissed=False):
        self.is_dismissed = is_dismissed
        self.answer = answer
        self.answer_ts = answer_ts
        self.question_id = question_id
        self.date_posted = func.now()

    def __repr__(self):
        return "<Answer {} {}>".format(self.answer,
                                       self.question_id)

    def save(self):
        """ Save pending """
        s = session.obtain_session()
        s.add(self)
        s.commit()

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

class Channel(Base):
    id = Column(Integer, primary_key=True)
    app_id = Column(String(230), unique=False)
    token = Column(String(230), unique=False)
    channel_id = Column(String(230), unique=False)
    team_id = Column(String(230), unique=False)
    user_id = Column(String(230), unique=False)
    date_added = Column(DateTime(timezone=True),
                                  server_default=func.now(),
                                  nullable=True,
                                  default=None)

    __tablename__ = "channel"

    def __init__(self, app_id=None,
                       channel_id=None,
                       token=None,
                       user_id=None,
                       team_id=None):
        self.app_id=app_id
        self.channel_id=channel_id
        self.token=token
        self.user_id=user_id
        self.team_id=team_id
        self.date_added = func.now()

    def save(self):
        """ Save channel """
        s = session.obtain_session()
        s.add(self)
        s.commit()

    def delete(self):
        """ Delete channel - no longer used """
        s = session.obtain_session()
        s.delete(self)
        s.commit()


    @staticmethod
    def find_by_app(app_id, token, team_id, user_id):
        """ Read latest mapping """
        s = session.obtain_session()
        m = s.query(Channel).filter(and_(Channel.app_id==app_id,
                                         Channel.token==token,
                                         Channel.team_id==team_id,
                                         Channel.user_id==user_id)).order_by(text('date_added')).first()
        s.commit()
        return m

    @staticmethod
    def delete_by_app(app_id, token, team_id, user_id):
        """ Delete by action id and token  """
        s = session.obtain_session()
        m = s.query(Channel).filter(and_(Channel.app_id==app_id,
                                         Channel.token==token,
                                         Channel.team_id==team_id,
                                         Channel.user_id==user_id)).order_by(desc('date_added')).first()

        s.delete(m)
        s.commit()

class Deletable(Base):
    id = Column(Integer, primary_key=True)
    message_ts = Column(String(230), unique=False)
    answer_compressed = Column(String(230), unique=False)
    question_compressed = Column(String(230), unique=False)
    channel_id =  Column(String(230), unique=False)
    date_added = Column(DateTime(timezone=True),
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
        s = session.obtain_session()
        s.add(self)
        s.commit()

    def delete(self):
        """ Delete pending - no longer used """
        s = session.obtain_session()
        s.delete(self)
        s.commit()
        s.flush()

    @staticmethod
    def latest_by_answer(answer):
        """ Read latest mapping """
        s = session.obtain_session()
        m = s.query(Deletable).filter(Deletable.answer_compressed==encode(answer)).first()
        return m

    @staticmethod
    def latest_by_question(question):
        """ Read latest mapping """
        s = session.obtain_session()
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

    @property
    def question(self):
        return decode(self.question_compressed)
 
    @property
    def answer(self):
        return decode(self.answer_compressed)

    def save(self):
        """ Save pending """
        s = session.obtain_session()
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
        s = session.obtain_session()
        self.date_modified = func.now()
        query = s.query(Mapping).filter(and_(Mapping.id==self.id,
                                             Mapping.question_compressed==self.question_compressed))
        query.update({"date_modified": func.now(), "answer_compressed": self.answer_compressed}, synchronize_session=False)
        s.commit()

    @staticmethod
    def update_answer(question, answer):
        """ Mark as answered """
        s = session.obtain_session()
        query = s.query(Mapping).filter(Mapping.question_compressed == encode(question))
        query.update({"date_modified": func.now(), "answer_compressed": encode(answer)}, synchronize_session=False)
        s.commit()


    @staticmethod
    def latest():
        """ Read latest mapping """
        s = session.obtain_session()
        q = s.query(Mapping).order_by(desc('date_modified')).first()
        return q


    @staticmethod
    def find_by_question(question):
        """ Read latest mapping """
        s = session.obtain_session()
        m = s.query(Mapping).filter(Mapping.question_compressed==encode(question)).order_by(desc('date_modified')).first()
        return m


    @staticmethod
    def find_by_answer(answer):
        """ Read latest mapping """
        s = session.obtain_session()
        q = s.query(Mapping).filter(Mapping.answer_compressed==encode(answer)).order_by(desc('date_modified')).first()
        return q


    @staticmethod
    def find(self, id):
        """ Read latest unanswered """
        s = session.obtain_session()
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
        s = session.obtain_session()
        s.add(self)
        s.commit()
    

    @staticmethod
    def latest_answered():
        """ Read latest answered """
        s = session.obtain_session()
        q = s.query(Pending).filter(Pending.date_answered!=None).order_by(desc('date_asked')).first()
        return q
    

    @staticmethod
    def latest():
        """ Read latest unanswered """
        s = session.obtain_session()
        q = s.query(Pending).filter(Pending.date_answered==None).order_by(desc('date_asked')).first() 
        return q


    @staticmethod
    def latest_by_question(question):
        """ Read latest mapping """
        s = session.obtain_session()
        q = s.query(Pending).filter(Pending.question==question).order_by(desc('date_asked')).first()
        return q


    def mark_as_answered(self):
        """ Mark as answered """
        s = session.obtain_session()
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
