#################
#### imports ####
#################
from datetime import datetime
from flask import Blueprint, Flask, json, jsonify, render_template, request, url_for, make_response
from flask import current_app
from flasgger import Swagger
from flask_api import status    # HTTP Status Codes
from werkzeug.local import LocalProxy

from models.users import User, UserSchema
from utils.session import obtain_session

users_blueprint = Blueprint('users', __name__, template_folder='templates')

logger = LocalProxy(lambda: current_app.logger)


@users_blueprint.route("/users/<int:id>", methods=['GET'])
def get_users(id):
    """
    Retrieve a single User
    This endpoint will return a User based on it's id
    ---
    tags:
      - Users
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of user to retrieve
        type: integer
        required: true
    responses:
      200:
        description: User returned
        schema:
          $ref: '#/definitions/User'
      404:
        description: User not found
    """
    try:
        sess = obtain_session()
        logger.debug(f"Trying to read user {id}")
        user = sess.query(User).get(id)
        user_schema = UserSchema(many=False)
        result = user_schema.dump(user)
        return make_response(jsonify(result), status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error reading the user {id} - {e}")
        result = {"error": str(e)}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)


@users_blueprint.route("/users", methods=['GET'])
def list_users():
    """
    Retrieve a list of Users
    This endpoint will return all Users unless a query parameter is specificed
    ---
    tags:
      - Users
    description: The Users endpoint allows you to query Users
    definitions:
      User:
        type: object
        properties:
            first_name:
              type: string
              description: First name for the user
            last_name:
              type: string
              description: Last name of the user
            email:
              type: string
              description: Email of the user
            username:
              type: string
              description: Username of the user
            password:
              type: string
              description: Password of the user
    responses:
      200:
        description: An array of Users
        schema:
          type: array
          items:
            schema:
              $ref: '#/definitions/User'
    """
    sess = obtain_session()
    all_users  = sess.query(User).all()
    users_schema = UserSchema(many=True)
    result = users_schema.dump(all_users)
    return make_response(jsonify(result), status.HTTP_200_OK)



@users_blueprint.route("/users/<int:id>", methods=['DELETE'])
def delete_user(id):
    """
    Delete a User
    This endpoint will delete a User based the id specified in the path
    ---
    tags:
      - Users
    description: Deletes a User from the database
    parameters:
      - name: id
        in: path
        description: ID of user to delete
        type: integer
        required: true
    responses:
      204:
        description: User deleted
    """
    try:
        sess = obtain_session()
        user = sess.query(User).get(id)

        if user:
            sess.delete(user)
            sess.commit()

        result = {"result": "success"}
        logger.debug(f"Successfully deleted user {id}")
        return make_response(jsonify(result),  status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error deleting user {id} - {e}")
        result = {"error": str(e)}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)


@users_blueprint.route("/users/<int:id>", methods=['PUT'])
def update_user(id):
    """
    Update a User
    This endpoint will update a User based the body that is posted
    ---
    tags:
      - Users
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of user to retrieve
        type: integer
        required: true
      - in: body
        name: body
        schema:
          id: data
          required:
            - name
            - category
          properties:
            first_name:
              type: string
              description: First name for the user
            last_name:
              type: string
              description: Last name of the user
            email:
              type: string
              description: Email of the user
            username:
              type: string
              description: Username of the user
            password:
              type: string
              description: Password of the user
    responses:
      200:
        description: User Updated
        schema:
          $ref: '#/definitions/User'
      400:
        description: Bad Request (the posted data was not valid)
    """
    data = request.json

    sess = obtain_session()

    try:
        user = sess.query(User).get(id)

        if not user:
            raise NotFound("User with id '{}' was not found.".format(id))

        user.password = data.get('password', user.password)
        user.bio = data.get('bio', user.bio)
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.username = data.get('username', user.username)
        sess.commit()

        user_schema = UserSchema(many=False)
        result = user_schema.dump(user)
        logger.debug(f"Successfully updated user {id}")
        return make_response(jsonify(result),  status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error updading user {id} - {e}")
        result = {"error": str(e)}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)


@users_blueprint.route("/users", methods=['POST'])
def create_user():
    """
    Creates a User
    This endpoint will create a User based the data in the body that is posted
    ---
    tags:
      - Users
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: data
          required:
            - account
            - category
            - password
          properties:
            first_name:
              type: string
              description: First name for the user
            last_name:
              type: string
              description: Last name of the user
            email:
              type: string
              description: Email of the user
            username:
              type: string
              description: Username of the user
            password:
              type: string
              description: Password of the user
    responses:
      201:
        description: User created
        schema:
          $ref: '#/definitions/User'
      400:
        description: Bad Request (the posted data was not valid)
    """
    try:
        data = request.json
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        username = data.get("account", "")
        password = data.get("password", "")
        category = data.get("category", "user")
        email = data.get("email", "")

        user = User(first_name=first_name,
                    last_name=last_name,
                    email=email,
                    category=category,
                    username=username,
                    password=password,
                    is_active=True,
                    is_staff=False)

        s = obtain_session()
        s.add(user)
        s.commit()
        s.flush()
        logger.debug(f"Saved new user {username} - {first_name} {last_name}")
        sess = obtain_session()
        all_users  = sess.query(User).all()
        users_schema = UserSchema(many=True)
        result = users_schema.dump(all_users)
        return make_response(jsonify(result), status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Failed saving user - {e}")
        result = {"error": str(e)}
        return make_response(jsonify(result), status.HTTP_500_INTERNAL_SERVER_ERROR)
