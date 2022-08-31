import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()
    except BaseException:
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    }, 200)



@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = Drink.query.all()
    except BaseException:
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    }, 200)

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    body = request.get_json()

    drink = Drink(
        title=body['title'],
        recipe=json.dumps(body['recipe'])
    )

    try:
        drink.insert()
    except BaseException:
        abort(400)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    body = request.get_json()

    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if not drink:
        abort(404)

    try:
        title = body.get('title')
        recipe = body.get('recipe')

        if title:
            drink.title = title

        if recipe:
            drink.recipe = json.dumps(recipe)

        drink.update()

    except BaseException:
        abort(422)

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    }), 200


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    try:
        drink.delete()
    except:
        abort(422)

    return jsonify({
        'success': True,
        'delete': id
        }), 200


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(400)
def  bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
        }), 404

@app.errorhandler(405)
def  method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405

@app.errorhandler(500)
def  server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server errror"
    }), 500

@app.errorhandler(AuthError)
def auth_error(err):
    return jsonify({
        "success": False,
        "error": err.status_code,
        "message": err.error
    })
