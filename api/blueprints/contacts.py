#################
#### imports ####
#################
from datetime import datetime
from flask import Blueprint, Flask, jsonify, render_template, request, url_for, make_response
from flask import current_app
from flasgger import Swagger
from flask_api import status    # HTTP Status Codes
from flask_cors import CORS, cross_origin
from werkzeug.local import LocalProxy

from models.contacts import Contact, ContactSchema
from utils.session import obtain_session

logger = LocalProxy(lambda: current_app.logger) 
contacts_blueprint = Blueprint('contacts', __name__, template_folder='templates')

@contacts_blueprint.route("/contacts/<int:id>", methods=['GET']) 
def get_contacts(id):
    """
    Retrieve a single Contact
    This endpoint will return a Contact based on it's id
    ---
    tags:
      - Contacts
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of contact to retrieve
        type: integer
        required: true
    responses:
      200:
        description: Contact returned
        schema:
          $ref: '#/definitions/Contact'
      404:
        description: Contact not found
    """
    return make_response(jsonify({"message": f"Contacts, all contacts"}), status.HTTP_200_OK)


@contacts_blueprint.route("/contacts", methods=['GET'])
def list_contacts():
    """
    Retrieve a list of Contacts
    This endpoint will return all Contacts unless a query parameter is specificed
    ---
    tags:
      - Contacts
    description: The Contacts endpoint allows you to query Contacts
    parameters:
      - name: first_name
        in: query
        description: first name of the contact
        required: true
        type: string
      - name: last_name
        in: query
        description: last name of the contact
        required: true
        type: string
    definitions:
      Contact:
        type: object
        properties:
            first_name:
              type: string
              description: First name for the contact
            last_name:
              type: string
              description: Last name of the contact
            email:
              type: string
              description: Email of the contact
            phone:
              type: string
              description: Phone of the contact
            username:
              type: string
              description: Username of the contact
    responses:
      200:
        description: An array of Contacts
        schema:
          type: array
          items:
            schema:
              $ref: '#/definitions/Contact'
    """
    results = []
    return make_response(jsonify(results), status.HTTP_200_OK)


@contacts_blueprint.route("/contacts/<int:id>", methods=['DELETE']) 
def delete_contact(id):
    """
    Delete a Contact
    This endpoint will delete a Contact based the id specified in the path
    ---
    tags:
      - Contacts
    description: Deletes a Contact from the database
    parameters:
      - name: id
        in: path
        description: ID of contact to delete
        type: integer
        required: true
    responses:
      204:
        description: Contact deleted
    """
    return make_response('', status.HTTP_204_NO_CONTENT)


@contacts_blueprint.route("/contacts/<int:id>", methods=['PUT'])
def update_contact(id):
    """
    Update a Contact
    This endpoint will update a Contact based the body that is posted
    ---
    tags:
      - Contacts
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of contact to retrieve
        type: integer
        required: true
      - in: body
        name: body
        schema:
          id: data
          required:
            - username
            - email
            - phone
          properties:
            first_name:
              type: string
              description: First name for the contact
            last_name:
              type: string
              description: Last name of the contact
            username:
              type: string
              description: Contactname of the contact
            email:
              type: string
              description: Email of the contact
            phone:
              type: string
              description: Phone of the contact
    responses:
      200:
        description: Contact Updated
        schema:
          $ref: '#/definitions/Contact'
      400:
        description: Bad Request (the posted data was not valid)
    """
    return make_response(jsonify([]), status.HTTP_200_OK)


@contacts_blueprint.route("/contacts", methods=['POST'])
def create_contact():
    """
    Create a new Site
    This endpoint will return a Site with any pages and forms parsed
    ---
    tags:
      - Contacts
    consumes:
      - application/json
    produces:
      - application/json
      - in: body
        name: body
        required: true
        schema:
          id: data
          required:
            - username
            - email
            - phone
          properties:
            username:
              type: string
              description: Username
            first_name:
              type: string
              description: First Name
            last_name:
              type: string
              description: Last Name
            phone:
              type: string
              description: Phone
            email:
              type: email
              description: Email
    responses:
      200:
        description: Contact returned
        schema:
          $ref: '#/definitions/Contact'
      404:
        description: Contact not found
    """

    return make_response(jsonify([]), status.HTTP_201_CREATED,
                         {'Location': '' })
