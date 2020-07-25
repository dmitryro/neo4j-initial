from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import ModelSchema
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from flask_marshmallow import Marshmallow

Base = declarative_base()
app = Flask(__name__, instance_relative_config=True)
ma = Marshmallow(app)



class State(Base):
    __tablename__ = 'states'
    id = Column(Integer, primary_key=True)
    name = Column(String(256), unique=False) 
    code = Column(String(2), unique=False)
    def __repr__(self):
        return "<State {}, {}, {}>".format(self.id,
                                           self.name,
                                           self.code)


class StateSchema(ModelSchema):
    """ Use this schema to serialize states """
    class Meta:
        model = State
