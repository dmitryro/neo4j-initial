import enum
from flask import Flask
from marshmallow_sqlalchemy import ModelSchema
from flask_marshmallow import Marshmallow
from flask_marshmallow.fields import fields
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()

app = Flask(__name__, instance_relative_config=True)
ma = Marshmallow(app)


class ImportanceEnum(enum.Enum):
    low = 'LOW' 
    moderate = 'MODERATE'
    medium = 'MEDIUM' 
    elevated = 'ELEVATED'
    high = 'HIGH'
    urgent = 'URGENT'


class SeveretyEnum(enum.Enum):
    low = 'LOW' 
    mild = 'MILD'
    medium = 'MEDIUM' 
    elevated = 'ELEVATED'
    high = 'HIGH'
    danger = 'DANGER'
    severe = 'SEVERE'
    disaster = 'DISASTER'



class LogType(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(20), unique=True)
    code = Column(String(20), unique=True)

    __tablename__ = "logtypes"

    def __init__(self, type=None, code=None):
        self.code = code
        self.type = type

    def __repr__(self):
        return "<LogType {} {}>".format(self.code,
                                        self.type)




class FormField(Base):
    """ Form Field """
    id = Column(Integer, primary_key=True, autoincrement=True)
    field_id = Column(String(256), unique=False)
    field_name = Column(String(256), unique=False)
    field_type = Column(String(256), unique=False)
    field_placeholder = Column(String(256), unique=False)
    field_value = Column(String(2256), unique=False)
    form_id = Column(Integer, ForeignKey("forms.id"), unique=False, nullable=False)
    action_id = Column(Integer, unique=False, nullable=True)
    actions = relationship("Action", secondary="action_formfield_link")

    __tablename__ = "formfields"

    def __init__(self, field_id=None, field_name=None, field_value=None,
                form_id=None, field_type=None, field_placeholder=None):
        self.field_id = field_id
        self.field_name = field_name
        self.field_value = field_value
        self.form_id = form_id
        self.field_type = field_type
        self.field_placeholder = field_placeholder

    def __repr__(self):
        return "<FormField {} {} {}>".format(self.field_id,
                                             self.field_name,
                                             self.field_valuer)



class Form(Base):
    """ Form """
    id = Column(Integer, primary_key=True, autoincrement=True)
    form_id = Column(String(256), unique=False)
    name = Column(String(256), unique=False)
    method = Column(String(256), unique=False)
    body = Column(String(2256), unique=False)
    page_id = Column(Integer, ForeignKey("pages.id"), unique=False, nullable=False)
    action = Column(String(2256), unique=False, nullable=True)
    action_id = Column(Integer, unique=False, nullable=True)
    actions = relationship("Action", secondary="action_form_link")

    __tablename__ = "forms"

    def __init__(self, form_id=None,
                       name=None,
                       method=None,
                       action=None,
                       body=None,
                       page_id=None):
        self.action = action
        self.name = name
        self.body = body
        self.method = method
        self.form_id = form_id
        self.page_id = page_id

    def __repr__(self):
        return "<Form {} {}>".format(self.name,
                                     self.body)


class Rule(Base):
    """ Form Field """
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), unique=False)
    code = Column(String(256), unique=False)
    is_active = Column(Boolean, unique=False, default=True)
    actions = relationship("Action", secondary="action_rule_link")
    severety = Column(String(30), unique=False, nullable=True)
    when_created = Column(DateTime(timezone=True), server_default=func.now())

    __tablename__ = "rules"

    def __init__(self,
                 name=None,
                 code=None,
                 severety='medium',
                 when_created=func.now(),
                 is_active=True):
        self.name = name
        self.code = code
        self.is_active = is_active
        self.severety = severety
        self.when_created = when_created

    def __repr__(self):
        return "<Rule {} {} {} {} {}>".format(self.code,
                                              self.name,
                                              self.severety,
                                              self.when_created,
                                              self.is_active)



class Action(Base):
    """ Form Field """
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_key = Column(String(256), unique=False)
    name = Column(String(256), unique=False)
    is_running =  Column(Boolean, unique=False)
    last_run = Column(DateTime(timezone=True), server_default=func.now())
    rules = relationship("Rule", secondary="action_rule_link")
    forms = relationship("Form", secondary="action_form_link")
    formfields = relationship("FormField", secondary="action_formfield_link")

    __tablename__ = "actions"

    def __init__(self, profile_key=None, name=None, 
                 form_id =  None,
                 form_field_id = None,
                 is_running = False, last_run=func.now()):
        self.profile_key = profile_key
        self.name = name
        self.is_running = is_running
        self.last_run = last_run
        self.form_id = form_id
        self.field_id = field_id

    def __repr__(self):
        return "<Action {} {} {} {} {} {}>".format(self.profile_key,
                                                   self.name,
                                                   self.is_running,
                                                   self.last_run,
                                                   self.form_id,
                                                   self.form_field_id)


class Event(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    took_place_at = Column(DateTime(timezone=True), server_default=func.now())
    severety = Column(String(30), nullable=False)
    importance = Column(String(30), nullable=False)
    description = Column(String(1000), unique=False)
    title = Column(String(300), unique=False)
    action_id = Column(Integer, ForeignKey('actions.id', ondelete='CASCADE'))
    field_id = Column(Integer, ForeignKey("formfields.id", ondelete='CASCADE'), unique=False, nullable=True)
    field = relationship("FormField")
    action = relationship('Action')

    __tablename__ = "events"

    def __init__(self, title=None, description=None, 
                 recorded_at=func.now(), took_place_at=func.now(),
                 importance=None,
                 severety=None,
                 action_id=None,
                 field_id=None):
        self.took_place_at=took_place_at
        self.recorded_at=recorded_at
        self.importance=importance
        self.description=description
        self.title=title
        self.severety=severety
        self.action_id=action_id
        self.field_id=field_id 

    def __repr__(self):
        return "<Event {} {} {} {} {}>".format(self.title,
                                               self.description,
                                               self.severety,
                                               self.importance,
                                               self.recorded_at)


class LogEntry(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    severety = Column(String(30), nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    header = Column(String(300), unique=False)
    body = Column(String(1000), unique=False)
    type_id = Column(Integer, ForeignKey("logtypes.id", ondelete='CASCADE'), unique=False, nullable=False)
    profile_key = Column(String(100))
    ip = Column(String(30), nullable=True,  default='0.0.0.0')
    action_id = Column(Integer, ForeignKey("actions.id", ondelete='CASCADE'), unique=False, nullable=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete='CASCADE'))
    action = relationship("Action")
    event = relationship("Event")
    log_type = relationship("LogType")
    
    __tablename__ = "logentries"


    def __init__(self,
                 severety=None,
                 event_id=None,
                 body=None,
                 header=None,
                 ip='0.0.0.0',
                 recorded_at=func.now(),
                 type_id=None,
                 profile_key=None,
                 action_id=None):
        self.recorded_at = recorded_at
        self.type_id = type_id
        self.body = body
        self.ip=ip
        self.header = header
        self.action_id = action_id
        self.profile_key = profile_key
        self.severety = severety
        self.event_id=event_id

    def __repr__(self):
        return "<LogEntry {} {} {} {}>".format(self.level,
                                               self.recorded_at,
                                               self.body,
                                               self.type_id,
                                               self.profile_key,
                                               self.action_id)


class Script(Base):
    """ Form Field """
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_key = Column(String(256), unique=False)
    code = Column(String(10000), unique=False)
    version = Column(Float, nullable=True, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __tablename__ = "scripts"


    def __init__(self, code=None,
                       version=1.0,
                       profile_key=None,
                       created_at=func.now()):
        self.code = code
        self.version = version
        self.profile_key = profile_key
        self.created_at = created_at

    def __repr__(seld):
        return f"<Script {self.code} {self.version} {self.profile_key} {self.time_created}>"


class ActionRuleLink(Base):
    __tablename__ = 'action_rule_link'
    id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey('actions.id'))
    rule_id = Column(Integer, ForeignKey('rules.id'))
    # ... any other fields
    #rule_actions = relationship(Action, backref=backref("actions", cascade="all, delete-orphan"))
    #actions = relationship(Action, backref=backref("rules", cascade="all, delete-orphan"))

    #rules = relationship(Rule, backref=backref("rules", cascade="all, delete-orphan"))


class FormLink(Base):
    __tablename__ = 'action_form_link'
    id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey('actions.id'))
    form_id = Column(Integer, ForeignKey('forms.id'))
    # ... any other fields
    #form_actions = relationship(Action, backref=backref("actions", cascade="all, delete-orphan"))
    forms = relationship(Form, backref=backref("forms", cascade="all, delete-orphan"))


class FormFormFieldLink(Base):
    __tablename__ = 'form_formfield_link'
    id = Column(Integer, primary_key=True)
    form_id = Column(Integer, ForeignKey('actions.id', ondelete='CASCADE'))
    formfield_id = Column(Integer, ForeignKey('forms.id', ondelete='CASCADE'))
    # ... any other fields
    #form_actions = relationship(Action, backref=backref("actions",cascade="all, delete-orphan"))
    #formsfields = relationship(FormField, backref=backref("formsfields", cascade="all, delete-orphan"))


class FormFieldLink(Base):
    __tablename__ = 'action_formfield_link'
    id = Column(Integer, primary_key=True)
    action_id = Column(Integer, ForeignKey('actions.id', ondelete='CASCADE'))
    formfield_id = Column(Integer, ForeignKey('formfields.id', ondelete='CASCADE'))
    # ... any other fields
    #formfield_actions = relationship(Action, backref=backref("actions", cascade="all, delete-orphan"))
    #formfields = relationship(Form, backref=backref("formsfields", cascade="all, delete-orphan"))


class RuleSchema(ModelSchema):
    """ Use this schema to serialize rules """
    class Meta:
        fields = ("id", "code", "name", "is_active", 'severety', 'when_created',)


class FormFieldSchema(ModelSchema):
    """ Use this schema to serialize formfields """
    class Meta:
        fields = ("id", "field_id", "field_nname", "field_type",
                  "field_placeholder", "field_value", "form_id",)


class LogTypeSchema(ModelSchema):
    class Meta:
        fields = ("id", "type", "code",)


class FormSchema(ModelSchema):
    """ Use this schema to serialize forms """
    fields = fields.Nested(FormFieldSchema)

    class Meta:
        fields = ("id", "form_id", "name", "method", "body", "page_id", "action",)


class ScriptSchema(ModelSchema):
    class Meta:
        fields = ("id", "profile_key", "code", "version",
                  "created_at",)


class ActionSchema(ModelSchema):
    """ Use this schema to serialize actions """
    rules = fields.Nested(RuleSchema)
    forms = fields.Nested(FormSchema)
    fields = fields.Nested(FormFieldSchema)

    class Meta:
        fields = ("id", "profile_key", "name", "is_running", "last_run",)


class EventSchema(ModelSchema):
    field = fields.Nested(FormFieldSchema)
    action = fields.Nested(ActionSchema)

    class Meta:
        fields = ("id", "recorded_at", "took_place_at", "severety", 
                  "importance", "description", "title", "action_id",)


class LogEntrySchema(ModelSchema):
    field = fields.Nested(FormFieldSchema)
    event = fields.Nested(EventSchema)
    log_type = fields.Nested(LogTypeSchema)
    action = fields.Nested(ActionSchema)
    class Meta:
        fields = ("id", "severety", "recorded_at", "header", "body", "type_id", "profile_key", 'action_id', 'event_id', "ip",)
