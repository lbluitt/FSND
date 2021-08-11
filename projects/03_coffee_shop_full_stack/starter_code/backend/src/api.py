import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from functools import wraps
from jose import jwt
from urllib.request import urlopen

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

AUTH0_DOMAIN = "lbluitt.us.auth0.com"
ALGORITHMS = ['RS256']
API_AUDIENCE = "https://coffee-shop/"


"""
https://lbluitt.us.auth0.com/authorize?audience=https://coffee-shop/&response_type=token&client_id=5xJNGBVEMk98W6K8jOynNdaiMILF1Qjk&redirect_uri=https://127.0.0.1:8080/login-results

{ex:https://coffeeshop.auth0.com}/authorize?audience={your_APIaudience}&response_type=token&client_id={your_ClientId}&redirect_uri={ex:http://127.0.0.1:8080/login-results}

https://lbluitt.us.auth0.com/authorize?audience=https://coffee-shop/&response_type=token&client_id=AKldA7rlnK866Ipyev73ckd2qAgsY0K0&redirect_uri=http://localhost:8100

"""

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks') 
def get_drinks():
    '''
    Get the list of all available drinks represented using the short drink representation
    note: this is a public endpoint, don't require any authentication
    '''
    
    try:
        drinks=Drink.query.order_by(Drink.id).all()
        drinks_formatted= []
        for drink in drinks:
            drinks_formatted.append(drink.short())
            
        return jsonify({
            "success": True,
            "drinks": drinks_formatted
        })
    except:
        abort(422)



'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt_token_payload):
    '''
    Get the list of all drinks represented using the long drink representation
    '''
    try:
        drinks = Drink.query.order_by(Drink.id).all()

        drinks_formatted=[drink.long() for drink in drinks] 

        return jsonify({
            "success":True,
            "drinks":drinks_formatted
        })
    except AuthError:
        abort(422)



'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks',methods=['POST'])
@requires_auth('post:drinks')
def post_drink(jwt_token_payload):
    '''
    Post a new drink 
    note: drinks' titles must be unique so new drinks must have titles that are not included in existing drinks
    '''
    body = request.get_json()

    if body is None:
        abort(422)

    try:

        title=body.get('title',None)
        recipe=body.get('recipe',None)

        new_drink=Drink(title=title,recipe=json.dumps(recipe))
        new_drink.insert()

        return jsonify({
            "success":True,
            "drinks":[new_drink.long()]
        })
    except Exception as err:
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(jwt_token_payload,id):
    '''
    Patch a drink by its id
    '''
    body = request.get_json()

    if body is None:
        abort(404)

    title= body.get('title',None)
    recipe=body.get('recipe',None)

    drink=Drink.query.filter(Drink.id==id).one_or_none()

    if not drink:
        abort(404)

    try:

        if title:
            drink.title=title
        if recipe:
            drink.recipe(json.dumps(recipe))

        drink.update()

        return jsonify({
            "success":True,
            "drinks":[drink.long()]
        })
    except Exception as err:
        abort(422)



'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>',methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(jwt_token_payload,id):
    '''
    Delete a drink by its id
    '''

    drink=Drink.query.filter(Drink.id==id).one_or_none()

    if not drink:
        abort(404)
    
    try:
        drink.delete()

        return jsonify({
            "success":True,
            "delete":id
        })
    except Exception as err:
        abort(422)



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


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success":False,
        "error":404,
        "message":"resource not found"
    }),404

@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success":False,
        "error":500,
        "message":"server error"
    }),500

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(error_metadata):
    return jsonify({
        "success":False,
        "error":error_metadata.status_code,
        "message":error_metadata.error['code']
    }),error_metadata.status_code