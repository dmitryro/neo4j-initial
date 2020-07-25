from flask import Flask
from marshmallow_sqlalchemy import ModelSchema
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from flask_marshmallow import Marshmallow

Base = declarative_base()
app = Flask(__name__, instance_relative_config=True)
ma = Marshmallow(app)


class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    username = Column(String(256), unique=False)
    first_name = Column(String(256), unique=False)
    last_name = Column(String(256), unique=False)
    time_contacted = Column(DateTime(timezone=True),
                                     server_default=func.now())
    phone = Column(String(256), unique=False)
    email = Column(String(256), unique=False)
    message = Column(String(512), unique=False)

    def __repr__(self):
        return "<Contact {}, {}, {}, {}, {}, {}, {}, {}>".format(self.id,
                                                             self.first_name,
                                                             self.last_name,
                                                             self.time_contacted,
                                                             self.subject,
                                                             self.phone,
                                                             self.email,
                                                             self.message)

class ContactSchema(ModelSchema):
    """ Use this schema to serialize contacts """
    class Meta:
        model = Contact
