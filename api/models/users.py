from flask import Flask
from marshmallow_sqlalchemy import ModelSchema
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import *
from flask_marshmallow import Marshmallow
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
app = Flask(__name__, instance_relative_config=True)
ma = Marshmallow(app)



#class Address(Base):
#    __tablename__ = "addresses"
#    id = Column(Integer, primary_key=True)
#    address1 = Column(String(256), unique=False) 
#    address2 = Column(String(256), unique=False)
#    city = Column(String(256), unique=False) 
#    state_id = Column(Integer, ForeignKey('state.id'))
#    country = Column(String(256), unique=False) 
#    postal_zip = Column(String(256), unique=False) 

#   def __repr__(self):
#        return "<Address {}, {}, {}, {}, {}, {}>".format(self.address1,
#                                                         self.address2,
#                                                         self.city,
#                                                         self.state_id,
#                                                         self.country,
#                                                         self.postal_zip)

class User(Base):
    """ The user record to save in Postgres """

    id = Column(Integer, primary_key=True)
    first_name= Column(String(256), unique=False)
    last_name = Column(String(256), unique=False)
    username = Column(String(256), unique=True)
    email = Column(String(256), unique=True)
    category = Column(String(40), unique=False)
    password = Column(String(256), unique=False)
    bio = Column(String(2048), unique=False)
    is_active = Column(Boolean, unique=False)
    is_staff = Column(Boolean, unique=False)
    is_superuser = Column(Boolean, unique=False)
    last_login = Column(DateTime(timezone=True), 
                                server_default=func.now())
    date_joined = Column(DateTime(timezone=True),    
                                  server_default=func.now())

    __tablename__ = "users"

    def __init__(self, first_name=None, last_name=None,
                 username=None, email=None, bio=None, 
                 password=None,
                 category=None,
                 is_staff=False,
                 is_active=False,
                 is_superuser=False,
                 date_born=func.now(),
                 last_login=func.now(),
                 date_joined=func.now()):
        self.category = category
        self.password = password
        self.email = email
        self.is_superuser = is_superuser
        self.is_staff = is_staff
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.last_login = last_login
        self.is_active = is_active
        self.date_born = date_born
        self.date_joined = date_joined
        self.bio = bio

    def __repr__(self):
        return "<User {} {} {} {}>".format(self.username,
                                           self.first_name, 
                                           self.last_name, 
                                           self.is_active)


class UserSchema(ModelSchema):
    """ Use this schema to serialize users """
    class Meta:
        model = User



#class AddressSchema(ma.ModelSchema):
#    """ Use this schema to serialize addresses """
#    class Meta:
#        model = Address


