#################
#### imports ####
#################
from sqlalchemy.sql import func
from datetime import datetime
import logging

from flask import Blueprint, Flask, json, jsonify, render_template, request, url_for, make_response
from flask import current_app
from flask_cors import cross_origin
from flasgger import Swagger
from flask_api import status    # HTTP Status Codes
from flask_cors import CORS, cross_origin
from werkzeug.local import LocalProxy

from models.actions import ImportanceEnum, SeveretyEnum
from models.actions import Script, ScriptSchema
from models.actions import Rule, RuleSchema
from models.actions import Action, ActionRuleLink, ActionSchema
from models.actions import FormFieldLink, FormLink
from models.actions import Form, FormSchema
from models.actions import FormField, FormFieldSchema
from models.actions import LogType, LogTypeSchema
from models.actions import LogEntry, LogEntrySchema
from models.actions import Event, EventSchema
from utils.session import obtain_session

actions_blueprint = Blueprint('actions', __name__, template_folder='templates')

logger = LocalProxy(lambda: current_app.logger)

@actions_blueprint.route("/actions/<string:profile_key>", methods=['GET'])
def get_profile_actions(profile_key):
    """
    Retrieve a list of Actions for given profile key
    This endpoint will return all Actions unless a query parameter is specificed
    ---
    tags:
      - Actions
    description: The Actions endpoint allows you to query Actions
    definitions:
      Action:
        type: object
        properties:
            name:
              type: string
              description: Name of action
            profile_key:
              type: string
              description: Profile key 
            rules:
              type: array
              description: List of rules to apply
            forms:
              type: array
              description: List of forms to listen
            formfields:
              type: array
              description: List of form elements to listen
            is_running:
              type: boolean
              description: Running status
            last_run: 
              type: date
              description: Last time it ran
    responses:
      200:
        description: An array of Actions
        schema:
          type: array
          items:
            schema:
              $ref: '#/definitions/Action'
    """
    try:
        sess = obtain_session()
        results = []
        actions = sess.query(Action).filter(Action.profile_key==profile_key).all()
        sess.flush()

        for action in actions:
            rules = action.rules #sess.query(Action).filter(Action.id==id).all()
            forms = action.forms
            formfields = action.formfields
            action_schema = ActionSchema(many=False)
            form_schema = FormFieldSchema(many=True)
            formfield_schema = FormFieldSchema(many=True)
            rules_schema = RuleSchema(many=True)

            forms_result = form_schema.dump(forms)
            formfields_result = formfield_schema.dump(formfields)
            rules_result = rules_schema.dump(rules)

            result = action_schema.dump(action)
            result['forms'] = forms_result
            result['formfields'] = formfields_result
            result['rules'] = rules_result
            results.append(result)
        logger.debug(f"Successfully fetched action {id}")
        return make_response(jsonify(results), status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Failed reading action {id} - {e}")
        result = {"error": str(e)}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)


@actions_blueprint.route("/actions/<int:id>", methods=['PUT'])
def update_action(id):
    """
    Update a single Action
    This endpoint will update a Action based on it's id
    ---
    tags:
      - Actions
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of action to update
        type: integer
        required: true
    responses:
      200:
        description: Action returned
        schema:
          $ref: '#/definitions/Action'
      404:
        description: Action not found
    """
    try:
        sess = obtain_session()
        action = sess.query(Action).filter(Action.id==id).first()
        action_schema = ActionSchema(many=False)
        result = action_schema.dump(action)
        logger.debug(f"Successfully fetched action {id}")
        return make_response(jsonify(result), status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Failed reading action {id} - {e}")
        result = {"error": str(e)}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)


@actions_blueprint.route("/logs", methods=['GET'])
def read_logs():
    """
    Retrieve a list of Log Entries
    This endpoint will return all Actions unless a query parameter is specificed
    ---
    tags:
      - Log Entries
    description: The Log Entries endpoint allows you to query Log Entries
    definitions:
      LogEntry:
        type: object
        properties:
            severety:
              type: string
              description: Log Entry severety
            event_id:
              type: integer
              description: Related event id
    responses:
      200:
        description: An array of Log Entries
        schema:
          type: array
          items:
            schema:
              $ref: '#/definitions/LogEntry'
    """
    sess = obtain_session()
    all_logs  = sess.query(LogEntry).all()
    logentry_schema = LogEntrySchema(many=True)
    result = logentry_schema.dump(all_logs)
    event_schema = EventSchema(many=False)

    for i, log in enumerate(all_logs):
        event = sess.query(Event).filter(Event.id==log.event_id).first()
        if event:
            result[i]['event'] = event_schema.dump(log.event)

    logger.debug(f"Successfully fetched all the actions.")
    return make_response(jsonify(result), status.HTTP_200_OK)


@actions_blueprint.route("/logs/<int:id>", methods=['GET'])
def get_log(id):
    """
    Retrieve a single LogEntry
    This endpoint will return a Log Entry based on it's id
    ---
    tags:
      - Log Entries
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of log entry to retrieve
        type: integer
        required: true
    responses:
      200:
        description: Log Entry returned
        schema:
          $ref: '#/definitions/LogEntry'
      404:
        description: LogEntry not found
    """
    try:
        sess = obtain_session()
        logentry = sess.query(LogEntry).filter(LogEntry.id==id).first()
        logentry_schema = LogEntrySchema(many=False)
        result = logentry_schema.dump(logentry)
        logger.debug(f"Successfully fetched log entry {id}")
        return make_response(jsonify(result), status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Failed reading log entry {id} - {e}")
        result = {"error": str(e)}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)


@actions_blueprint.route("/logs/<int:id>", methods=['PUT'])
def update_log(id):
    """
    Update a single LogEntry
    This endpoint will update a Action based on it's id
    ---
    tags:
      - Log Entries
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of log entry to update
        type: integer
        required: true
    responses:
      200:
        description: LogEntry returned
        schema:
          $ref: '#/definitions/LogEntry'
      404:
        description: LogEntry not found
    """
    try:
        logentry_schema = LogEntrySchema(many=False)
        sess = obtain_session()
        logentry = sess.query(LogEntry).filter(LogEntry.id==id).first()
        result = logentry_schema.dump(logentry)
        logger.debug(f"Successfully updated log entry {id}")
        return make_response(jsonify(result), status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Failed reading log entry {id} - {e}")
        result = {"error": str(e)}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)


@actions_blueprint.route("/logs/<int:id>", methods=['DELETE'])
def delete_log(id):
    """
    Delete a Log Entry
    This endpoint will delete a Log Entry based the id specified in the path
    ---
    tags:
      - Log Entries
    description: Deletes a Log Entry from the database
    parameters:
      - name: id
        in: path
        description: ID of site to delete
        type: integer
        required: true
    responses:
      204:
        description: Log Entry deleted
    """
    try:
        sess = obtain_session()
        log = sess.query(LogEntry).get(id)
        logger.debug(f"Deleting log entry {id} ...")

        if log:
            sess.delete(log)
            sess.commit()
            sess.flush()
        result = {"result": "success"}
        return make_response(jsonify(result), status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Error deleting the site {id} - {e}")
        result = {"result": "failure"}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)


@actions_blueprint.route("/events", methods=['GET'])
def read_events():
    """
    Retrieve a list of Log Entries
    This endpoint will return all Actions unless a query parameter is
specificed
    ---
    tags:
      - Events
    description: The Events endpoint allows you to query Events
    definitions:
      Event:
        type: object
        properties:
            severety:
              type: string
              description: Event severety
            importance:
              type: string
              description: Event importance
            field_id:
              type: integer
              description: Related field id
    responses:
      200:
        description: An array of Log Entries
        schema:
          type: array
          items:
            schema:
              $ref: '#/definitions/LogEntry'
    """
    sess = obtain_session()
    all_events  = sess.query(Event).all()
    event_schema = EventSchema(many=False)
    result = event_schema.dump(all_events)
    formfield_schema = FormFieldSchema(many=False)
    action_schema = ActionSchema(many=False)

    try:
        all_events  = sess.query(Event).all()
        event_schema = EventSchema(many=False)
        
        for i, event in enumerate(all_events):
            field = sess.query(FormField).filter(FormField.id==event.field_id).first()
            action = sess.query(Action).filter(Action.id==event.action_id).first()
        #if field:
            #result[i]['field'] = formfield_schema.dump(field)
        #if action:
         #   result[i]['action'] = action_schema.dump(action)
        logger.debug(f"Successfully fetched all the actions.")
        return make_response(jsonify(result), status.HTTP_200_OK)
    except Exception as e:
        result = {"message":f"error - {e}"}
        logger.error(f"Could not read form field or action {e}")
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)



@actions_blueprint.route("/logs", methods=['POST'])
def record_log():
    """
    Creates a Log Entry
    This endpoint will generate a log entry based on profile key and severety.
    ---
    tags:
      - Log Entries
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: script_data
          required:
            - profile_key
            - severety
            - word
            - action_id
            - log_type_code
            - field_id
          properties:
            profile_key:
              type: string
              description: Profile Key
            severety:
              type: string
              description: Content severety
            importance:
              type: string
              description: Content importance
            word:
              type: string
              description: The actual word detected
            field_id:
              type: integer
              description: Field id of the field veing logged
            log_type_code:
              type: string
              description: Log type code to be used
            action_id:
              type: integer
              description: Action to be logged       
            ip:
              type: string
              description: Client's IP address
    responses:
      201:
        description: Script created
        schema:
          $ref: '#/definitions/Script'
      400:
        description: Bad Request (the posted data was not valid)
    """
    try:
        data = request.json
        profile_key = data.get("profile_key", None)
        log_type_code = data.get('log_type_code', None)
        severety = data.get("severety", None)
        ip = data.get("ip", "0.0.0.0")
        word = data.get("word", None)
        action_id = int(data.get("action_id", -1))
        field_id = data.get("field_id", None)
        importance = data.get("importance", None)
        logger.debug(f"==> Read the params {profile_key} - {log_type_code} - {severety} - {word} - {action_id} - {field_id}")

        if not field_id:
            raise NotFound("Field id '{field_id}' was not found.") 
        if not profile_key:
            raise NotFound("Product key '{profile_key}' was not found.")

        sess = obtain_session()
        field = sess.query(FormField).filter(FormField.field_id==field_id).first()

        if not field:
            raise NotFound("Field id '{field_id}' was not found.")         
 
        action = sess.query(Action).filter(Action.id==action_id).first()

        event = Event(title=f"detected {word}",
                      importance=importance,
                      severety=severety,
                      description=f"detected {word}",
                      action_id=action_id, 
                      field_id=field.id)


        sess.add(event)
        sess.commit()
        event_id = event.id
        sess.flush()
        event_id = event.id 
        logger.debug(f"==> Recorded event with id {event_id}")

        logtype = sess.query(LogType).filter(LogType.code==log_type_code).first()
        log = LogEntry(action_id=action.id,
                       event_id=event_id,
                       header=event.title,
                       ip=ip,
                       severety=severety,
                       body=event.description,
                       profile_key=profile_key,
                       type_id=logtype.id)

        sess.add(log) 
        sess.commit()
        sess.flush()
        result = {"message": "success"}
        logger.debug(f"Successfully generated script for {profile_key}")
        return make_response(jsonify(result), status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"==> It just didn't work - {e}")
        result = {"message": f"error {e}"}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)


@actions_blueprint.route("/scripts", methods=['POST'])
def generate_script():
    """
    Creates a Script
    This endpoint will create a Script based on profile key.
    ---
    tags:
      - Script
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: script_data
          required:
            - profile_key
          properties:
            profile_key:
              type: string
              description: Profile Key
    responses:
      201:
        description: Script created
        schema:
          $ref: '#/definitions/Script'
      400:
        description: Bad Request (the posted data was not valid)
    """
    try:
        data = request.json
        profile_key = data.get("profile_key", None)

        if not profile_key:
            raise NotFound("Product key '{profile_key}' was not found.")

        sess = obtain_session()
        code = ("<script>", f"let key = {profile_key};", 
                "(function run() {})();"
                "</script>")

        sc = Script(profile_key=profile_key,
                    code="".join(code),
                    version=1.0,
                    created_at=func.now())
        sess.add(sc)
        sess.commit()

        script_schema = ScriptSchema(many=False)
        result = script_schema.dump(sc)
        logger.debug(f"Successfully generated script for {profile_key}")
        return make_response(jsonify(result), status.HTTP_200_OK)
    except Exception as e:
        result = {"error": str(e)}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)
        

@actions_blueprint.route("/actions/<int:id>", methods=['GET'])
def get_actions(id):
    """
    Retrieve a single Action
    This endpoint will return a Action based on it's id
    ---
    tags:
      - Actions
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of action to retrieve
        type: integer
        required: true
    responses:
      200:
        description: Action returned
        schema:
          $ref: '#/definitions/Action'
      404:
        description: Action not found
    """
    try:
        sess = obtain_session()
        action = sess.query(Action).filter(Action.id==id).first()
        forms = sess.query(Form).join(Form.forms).filter_by(action_id=action.id).all() 
        #formfields = sess.query(FormField).join(Form.formfields).filter_by(action_id=action.id).all()
        rules = action.rules #sess.query(Action).filter(Action.id==id).all() #.rules.any(action_id=action.id)).all() 
        forms = action.forms
        formfields = action.formfields        
        #sess.query(Rule).join(ActionLink.rules).filter_by(action_id=action.id).all()
        action_schema = ActionSchema(many=False)
        form_schema = FormFieldSchema(many=True)
        formfield_schema = FormFieldSchema(many=True)
        rules_schema = RuleSchema(many=True)
        
        forms_result = form_schema.dump(forms)
        formfields_result = formfield_schema.dump(formfields)
        rules_result = rules_schema.dump(rules)

        result = action_schema.dump(action)
        result['forms'] = forms_result
        result['formfields'] = formfields_result
        result['rules'] = rules_result

        logger.debug(f"Successfully fetched action {id}")
        return make_response(jsonify(result), status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Failed reading action {id} - {e}")
        result = {"error": str(e)}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)


@actions_blueprint.route("/actions", methods=['GET'])
def list_actions():
    """
    Retrieve a list of Actions
    This endpoint will return all Actions unless a query parameter is specificed
    ---
    tags:
      - Actions
    description: The Actions endpoint allows you to query Actions
    definitions:
      Action:
        type: object
        properties:
            host:
              type: string
              description: Host of the action
            port:
              type: string
              description: Port of the action
    responses:
      200:
        description: An array of Actions
        schema:
          type: array
          items:
            schema:
              $ref: '#/definitions/Action'
    """
    sess = obtain_session()
    all_actions  = sess.query(Action).all()
    actions_schema = ActionSchema(many=True)
    result = actions_schema.dump(all_actions)

    forms_schema = FormFieldSchema(many=True)
    formfields_schema = FormFieldSchema(many=True)
    rules_schema = RuleSchema(many=True)

    for i, action in enumerate(all_actions):
        result[i]['rules'] = rules_schema.dump(action.rules) 
        result[i]['forms'] = forms_schema.dump(action.forms)
        result[i]['formfields'] = formfields_schema.dump(action.formfields)

    logger.debug(f"Successfully fetched all the actions.")
    return make_response(jsonify(result), status.HTTP_200_OK)


@actions_blueprint.route("/actions/<int:id>", methods=['DELETE'])
def delete_action(id):
    """
    Delete a Action
    This endpoint will delete a Action based the id specified in the path
    ---
    tags:
      - Actions
    description: Deletes a Action from the database
    parameters:
      - name: id
        in: path
        description: ID of action to delete
        type: integer
        required: true
    responses:
      204:
        description: Action deleted
    """
    try:
        sess = obtain_session()
        action = sess.query(Action).filter(Action.id==id).first()

        if action:
            sess.delete(action)
            sess.commit()
            sess.flush()
        logger.debug(f"Successfully deleted action {id}")
        result = {"result": "success"}
        return make_response(jsonify(result), status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Failed deleting action {id} - {e}")
        result = {"result": "failure"}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)


@actions_blueprint.route("/rules", methods=['GET'])
def list_rules():
    """
    Retrieve a list of Rules
    This endpoint will return all Rules unless a query parameter is specificed
    ---
    tags:
      - Rules
    description: The Rules endpoint allows you to query Rules
    definitions:
      Rules:
        type: object
        properties:
            id:
              type: integer
              description: id
            name:
              type: string
              description: Name of the rule
            code:
              type: string
              description: Pattern of the rule
            is_active:
              type: boolean
              description: Rule is active or not
            severety:
              type: string
              description: Severety level of the rule
            when_created:
              type: date
              description: The date the rule was created
    responses:
      200:
        description: An array of Actions
        schema:
          type: array
          items:
            schema:
              $ref: '#/definitions/Action'
    """

    sess = obtain_session()
    all_rules  = sess.query(Rule).all()
    rules_schema = RuleSchema(many=True)
    result = rules_schema.dump(all_rules)
    logger.debug(f"Successfully fetched all the actions.")
    return make_response(jsonify(result), status.HTTP_200_OK)


@actions_blueprint.route("/rules/<int:id>", methods=['GET'])
def get_rule(id):
    """
    Retrieve a single Rule
    This endpoint will return a Rule based on it's id
    ---
    tags:
      - Rules
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of action to retrieve
        type: integer
        required: true
    responses:
      200:
        description: Action returned
        schema:
          $ref: '#/definitions/Action'
      404:
        description: Action not found
    """
    try:
        sess = obtain_session()
        rule = sess.query(Rule).filter(Rule.id==id).first()
        actions = rule.actions
        rule_schema = RuleSchema(many=False)
        actions_schema = ActionSchema(many=True)
        actions_result = actions_schema.dump(actions)
        result = rule_schema.dump(rule)
        result['actions'] = actions_result
        logger.debug(f"Successfully fetched action {id}")
        return make_response(jsonify(result), status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Failed reading action {id} - {e}")
        result = {"error": str(e)}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)


@actions_blueprint.route("/rules", methods=['POST'])
def create_rule():
    """
    Creates a Rule
    This endpoint will create a Rule based the data in the body that is posted
    ---
    tags:
      - Rules
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: rule_data
          required:
            - name
            - code
          properties:
            name:
              type: string
              description: Rule name
            code:
              type: string
              description: Rule code
            severety:
              type: string
              description: Rule severety (low, medium, high)
            is_active:
              type: boolean
              description: Rule is active or not
    responses:
      201:
        description: Rule created
        schema:
          $ref: '#/definitions/Rule'
      400:
        description: Bad Request (the posted data was not valid)
    """
    try:
        data = request.json
        severety = data.get("severety", "medium")
        name = data.get("name", "detect")
        code = data.get("code", "")
        is_active = data.get("is_active", True)
        rule = Rule(code=code,
                    name=name,
                    when_created=func.now(),
                    is_active=bool(is_active),
                    severety=severety)
        s = obtain_session()
        s.add(rule)
        s.commit()
        rule_schema = RuleSchema(many=False)
        result = rule_schema.dump(rule)
        logger.debug(f"Saved new rule {name} {code}")
        return make_response(jsonify(result),  status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Failed saving site - {e}")
        result = {"result": "failure"}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)


@actions_blueprint.route("/rules/<int:id>", methods=['DELETE'])
def delete_rule(id):
    """
    Delete a Rule
    This endpoint will delete a Rule based the id specified in the path
    ---
    tags:
      - Rules
    description: Deletes a Action from the database
    parameters:
      - name: id
        in: path
        description: ID of rule to delete
        type: integer
        required: true
    responses:
      204:
        description: Rule deleted
    """
    try:
        sess = obtain_session()
        rule = sess.query(Rule).filter(Rule.id==id).first()
        if rule:
            sess.delete(rule)
            sess.commit()
            sess.flush()
        logger.debug(f"Successfully deleted rule {id}")
        result = {"result": "success"}
        return make_response(jsonify(result), status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.error(f"Failed deleting rule {id} - {e}")
        result = {"result": "failure"}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)


@actions_blueprint.route("/rules/<int:id>", methods=['PUT'])
def update_rule(id):
    """
    Update a Rule
    This endpoint will update a Rule based the body that is posted
    ---
    tags:
      - Rules
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of Rule to update
        type: integer
        required: true
      - in: body
        name: body
        schema:
          id: data
          required:
            - name
            - code
          properties:
            name:
              type: string
              description: Ru;e's name
            code:
              type: string
              description: Rule's code or pattern
            severety:
              type: string
              description: Rule's severety level
            is_active:
              type: boolean
              description: Rule is active or not
    responses:
      200:
        description: Contact Updated
        schema:
          $ref: '#/definitions/Contact'
      400:
        description: Bad Request (the posted data was not valid)
    """
    return make_response(jsonify([]), status.HTTP_200_OK)
