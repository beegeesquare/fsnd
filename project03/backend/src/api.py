"""
API's for Coffeeshop app
"""
from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS
import sys
from .database.models import setup_db, Drink
from .database.models import db_drop_and_create_all
from .auth.auth import requires_auth, AuthError
from sqlalchemy.exc import IntegrityError
app = Flask(__name__)
setup_db(app)
CORS(app)

# Use the after_request decorator to set Access-Control-Allow
# Basically this puts the header in the response
# CORS headers
@app.after_request
def after_request(response):
    """

    :param response:
    :return:
    """
    # Here it will tell the client if the content requires authorization or not
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    # Here in the response it will tell to the client what methods are allowed
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE')
    return response

# uncomment the following line to initialize the datbase
# NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
# NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN

# Disable this after the first run
db_drop_and_create_all()


# ROUTES
'''
@ implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def get_drinks():
    """
    List the drinks in the menu
    :return:
    """
    drinks = Drink.query.all()
    print(drinks)
    short_details = [d.short() for d in drinks]

    return jsonify({"success": True, "drinks":short_details})


'''
@implement endpoint
    GET /drinks-detail
    it should require the 'get:drinks-detail' permission
    it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_details(token):
    """
    Gives the brink recipes
    :param token: This is JWT token required for Bearer authorization
    :return:
    """
    drinks = Drink.query.all()
    long_details = [d.long() for d in drinks]

    return jsonify({"success": True, "drinks": long_details})


'''
@ implement endpoint
    POST /drinks
    it should create a new row in the drinks table
    it should require the 'post:drinks' permission
    it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly 
    created drink
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
#def add_new_drink():
def add_new_drink(token):
    """
    Add new drinks to the menu
    :param token: This is JWT token required for Bearer authorization
    :return:
    """
    # print(request.form, request.get_json(), request.get_data())
    data = request.get_json()
    # print(data)
    try:
        # id should auto increment
        new_recipe = data.get('recipe')
        new_title = data.get('title')
        # As per the database schema this title and recipe column cannot be null
        if (new_title is None) or (new_recipe is None):
            abort(422)

        if type(new_recipe) is not list:
            new_recipe = [new_recipe]
        try:
            new_drink = Drink(title=data.get('title'),
                              # Recipe has to be given as json dump
                              recipe=json.dumps(new_recipe)
                              )
            # This should add the data to the database table drink
            new_drink.insert()
            return jsonify({'success': True,
                            'drink': [new_drink.long()]})
        except IntegrityError: # Names should be unique
            abort(422)

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
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the 
    updated drink
    or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(token, drink_id):
    """
    Edit the drink recipe for the given ID
    :param token: This is JWT token required for Bearer authorization
    :param drink_id: This is the ID for the drink in the menu
    :return:
    """
    drink = Drink.query.get(drink_id)
    data = request.get_json()
    if drink:
        # If the patch method has no payload for title do not do anything
        if data.get('title') is not None:
            drink.title = data.get('title')
        # If the patch method has no payload for recipe do not do anything
        if data.get('recipe') is not None:
            # Json dumps is necessary for the drink table to parse
            drink.recipe = json.dumps(data.get('recipe'))
        # Update the respective drink for the given ID
        drink.update()
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })


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
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def remove_drink(token, drink_id):
    """
    Remove the drink for the menu
    :param token: This is JWT token required for Bearer authorization
    :param drink_id: Id for the drink in the menu
    :return:
    """
    drink = Drink.query.get(drink_id)
    if drink: # Means not None
        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id
        })

    return abort(404)


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(400)
def badrequest(error):
    """

    :param error:
    :return:
    """
    return jsonify({"success": False,
                    "error": 400,
                    "message": "bad request"}), 400


@app.errorhandler(422)
def unprocessable(error):
    """

    :param error:
    :return:
    """
    return jsonify({"success": False,
                    "error": 422,
                    "message": "unprocessable"}), 422


'''
@ implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
    jsonify({
    "success": False, 
    "error": 404,
    "message": "resource not found"
    }), 404
'''
@app.errorhandler(404)
def notfound(error):
    """

    :param error:
    :return:
    """
    return jsonify({"success": False,
                    "error": 404,
                    "message": "resource not found"}), 404


'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(401)
def notauthorized(AuthError):
    """

    :param AuthError:
    :return:
    """
    return jsonify({"success": False,
                    "error": 401,
                    "message": "Unauthorized"}), 401


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(403)
def nopermissions(error):
    """

    :param error:
    :return:
    """
    return jsonify({"success": False,
                    "error": 403,
                    "message": "Permissions not found"}), 403
