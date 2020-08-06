#################
#### imports ####
#################
from datetime import datetime
from flask import Blueprint, Flask, json, jsonify, render_template, request, url_for, make_response
from flask import current_app
from flasgger import Swagger
from flask_api import status    # HTTP Status Codes
from werkzeug.local import LocalProxy
from urllib import parse
from utils.session import obtain_session
from utils.process import process_block_actions, process_dialogs


slack_blueprint = Blueprint('slack', __name__, template_folder='templates')
logger = LocalProxy(lambda: current_app.logger)


@slack_blueprint.route("/api/interactive", methods=['POST'])
def slack_action():
    """
    Process action
    ---
    tags:
      - Actions
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
    responses:
      200:
        description: Site created
      400:
        description: Bad Request (the posted data was not valid)
    """
    try:
        prefix = "payload="
        data = request.get_data(as_text=True)[len(prefix):]
        # action body
        slack_req_body = json.loads(parse.unquote_plus(data))
        logger.info(f"ACTION BODY : {slack_req_body}")
        slack_req_type = slack_req_body.get("type")
        action = {"block_actions": process_block_actions, "view_submission": process_dialogs}
        response = action[slack_req_type](slack_req_body)
        logger.info("Response to Action: %s : %s", response, response.get_data())
        return response #make_response(jsonify(result), status.HTTP_200_OK)
    except Exception as e:
        logger.exception(f"A PROBLEM {e}")
        logger.error(f"Failed saving site - {e}")
        result = {"result": "failure"}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)


@slack_blueprint.route("/api/interactive", methods=['GET'])
def get_slack():
    """
    Retrieve a single Site
    This endpoint will return a Site based on it's id
    ---
    tags:
      - Slack
    produces:
      - application/json
    responses:
      200:
        description: Site returned
        schema:
          $ref: '#/definitions/Site'
      404:
        description: Site not found
    """
    try:
        result = {"message": "success"}
        logger.debug(f"Reading the Slack data ...")
        return make_response(jsonify(result), status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error reading the site {id} - {e}")
        result = {"error": str(e)}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)
















