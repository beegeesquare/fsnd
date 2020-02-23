import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError
import sys
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# Use the after_request decorator to set Access-Control-Allow
# Basically this puts the header in the response
# CORS headers
@app.after_request
def after_request(response):
    # Here it will tell the client if the content requires authorization or not
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    # Here in the response it will tell to the client what methods are allowed
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,PATCH,POST,DELETE,OPTIONS')
    return response

# TODO uncomment the following line to initialize the datbase
# NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
# NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN

# Disable this after the first run
# db_drop_and_create_all()


## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    print(drinks)
    short_details = [d.short() for d in drinks]

    return (jsonify({"success": True, "drinks":short_details}), 
            200)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(token):
    drinks = Drink.query.all()
    long_details = [d.long() for d in drinks]

    return (jsonify({"success": True, "drinks": long_details}), 200)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(token):
    print(request.form, request.get_json(), request.get_data())
    data = request.get_json()
    
    try:
        # id should auto increment
        new_drink = Drink(title= data.get('title'),
                          recipe=json.dumps(data.get('recipe')) # Recipe has to be given as json dump
                         )
        # This should add the data to the database table drink
        new_drink.insert()
        return jsonify({'success': True,
                    'drink': new_drink.long()})

    except KeyError:
        print(sys.exc_info())
        return abort(422)
    


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
@app.route('/drinks/<int:id>', methods=['PATCH'])
def update_drink(id):
    return

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
@app.route('/drinks/<int:id>', methods=['DELETE'])
def remove_drink(id):
    return


## Error Handling
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
@app.errorhandler(404)
def notfound(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(401)
def notauthorized(AuthError):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "Unauthorized"
                    }), 401


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''