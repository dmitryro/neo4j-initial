# Copyright 2019, 2020 Dmitry Roitman. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
import os
from flask import Flask, jsonify, request, url_for, make_response
from flask.logging import default_handler
from flasgger import Swagger
from flask_api import status    # HTTP Status Codes
#from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_alembic import Alembic
from logging.config import dictConfig
from werkzeug.exceptions import NotFound
from blueprints.users import users_blueprint
from blueprints.contacts import contacts_blueprint
from blueprints.states import states_blueprint
from blueprints.sites import sites_blueprint
from blueprints.actions import actions_blueprint

# Pull options from environment
debug = (os.getenv('DEBUG', 'False') == 'True')
port = os.getenv('PORT', '5000')
database_url = os.getenv('DATABASE_URL', 'postgresql+psycopg2://postgres:postgres@postgres:5432/postgres')
sqlalchemy_notifications = (os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False') == 'True')


def create_app():
    # Initialize Flask
    app = Flask(__name__)
    app.register_blueprint(users_blueprint)
    app.register_blueprint(contacts_blueprint)
    app.register_blueprint(states_blueprint)
    app.register_blueprint(sites_blueprint)
    app.register_blueprint(actions_blueprint)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = sqlalchemy_notifications
    # Configure Swagger before initilaizing it
    app.config['SWAGGER'] = {
        "swagger_version": "2.0",
        "specs": [
            {
                "version": "0.0.1",
                "title": "Flask API",
                "description": "This is a sample flask API using swagger",
                "endpoint": 'v1_spec',
                "route": '/v1/spec'
            }
        ]
    }
    return app

alembic = Alembic()
app = create_app()
# Initialize Swagger after configuring it
Swagger(app)
#CORS(app)


db = SQLAlchemy(app)
migrate = Migrate(app, db)
alembic.init_app(app)
alembic.rev_id = lambda: datetime.utcnow().timestamp()

######################################################################
# ERROR Handling
######################################################################
@app.errorhandler(ValueError)
def request_validation_error(e):
    """ Handles validation errors """
    return bad_request(e)

@app.errorhandler(404)
def not_found(e):
    """ Handles 404 Not Fund errors """
    return make_response(jsonify(status=404, error='Not Found',
                                 message=e.description), status.HTTP_404_NOT_FOUND)

@app.errorhandler(400)
def bad_request(e):
    """ Handles 400 Bad Requests """
    return make_response(jsonify(status=400, error='Bad Request',
                                 message=e.message), status.HTTP_400_BAD_REQUEST)

@app.errorhandler(405)
def method_not_allowed(e):
    """ Handles 405 Method Not Allowed """
    return make_response(jsonify(status=405, error='Method not Allowed',
                                 message='Your request method is not supported. Check your HTTP method and try again.'), status.HTTP_405_METHOD_NOT_ALLOWED)

@app.errorhandler(500)
def internal_error(e):
    """ Handles 500 Server Errors """
    return make_response(jsonify(status=500, error='Internal Server Error',
                                 message='Huston... we have a problem.'), status.HTTP_500_INTERNAL_SERVER_ERROR)


######################################################################
#  Index
######################################################################
@app.route("/")
def index():
    """ Home Page """
    return jsonify(name='REST API Service',
                   version='1.0',
                   docs=request.base_url + 'apidocs/index.html'), status.HTTP_200_OK


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port), debug=debug)
