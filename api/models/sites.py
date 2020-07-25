from flask import Flask
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import ModelSchema
from flask_marshmallow.fields import fields
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from models.actions import FormSchema, FormFieldSchema

Base = declarative_base()
app = Flask(__name__, instance_relative_config=True)
ma = Marshmallow(app)

class Site(Base):
    """ The site record to save in Postgres """

    id = Column(Integer, primary_key=True, autoincrement=True)
    host = Column(String(1256), unique=False)
    port = Column(Integer, default=80)
    ip = Column(String(256), unique=True)
    ga = Column(String(50), unique=False, nullable=True)
    date_added = Column(DateTime(timezone=True),
                                 server_default=func.now())
    date_last_crawled = Column(DateTime(timezone=True),    
                               server_default=func.now())


    __tablename__ = "sites"

    def __init__(self, host=None, port=None,
                 ga=None, date_added=func.now(),
                 date_last_crawled=func.now()):
        self.ga = ga
        self.host = host
        self.port = port
        self.ip = '127.0.0.1'
        self.date_added = date_added
        self.date_last_crawled = date_last_crawled
        

    def __repr__(self):
        return "<Site {} {} {} {} {}>".format(self.id,
                                              self.host,
                                              self.port,
                                              self.ip,
                                              self.date_last_crawled)



class Page(Base):
    """ The site page """
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), unique=False)
    meta = Column(String(1256), unique=False)
    headers = Column(String(1256), unique=False)
    site_id = Column(Integer, ForeignKey(Site.id, ondelete='CASCADE'), unique=True, nullable=False)

    __tablename__ = "pages"


    def __init__(self, name=None, meta=None, headers=None, site_id=None):
        self.name = name
        self.meta = meta
        self.headers = headers
        self.site_id = site_id

    def __repr__(self):
        return "<Page {} {} {} {} {}>".format(self.id,
                                              self.name,
                                              self.meta,
                                              self.headers,
                                              self.site_id)


class PageSchema(ModelSchema):
    """ Use this schema to serialize pages """
    forms = fields.Nested(FormSchema)

    class Meta:
        fields = ("id", "name", "meat", "headers", "site_id",)


class SiteSchema(ModelSchema):
    """ Use this schema to serialize sites """
    pages = fields.Nested(PageSchema)

    class Meta:
        model = Site





