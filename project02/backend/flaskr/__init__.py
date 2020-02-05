import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


# define pagination
def paginate_questions(request, query_all):
    page = request.args.get('page', 1, type=int)
    start = (page -1)*QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [q.format() for q in query_all]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    CORS(app, resources={r'/api/*': {"origins": "*"}})

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

    @app.route('/')
    def index():
        return "Welcome to Trivia"

    # Create an endpoint to handle GET requests for all available categories.
    @app.route('/categories')
    def list_categories():
        categories = Category.query.order_by(Category.id).all()
        # data = [c.format() for c in categories] # format method is defined in Category model
        # return jsonify({'success': True, 'categories': data,
                        # 'total_categories': len(Category.query.all())
                        # })
        # Format has been changed to render the fronend correctly
        return jsonify({'success':True, 'categories': {c.id: c.type for c in categories}})

    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 
  
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({'success': True,
                        'questions': current_questions,
                        'total_questions': len(questions),
                        # This has to be a dictionary for the frontend to render the UI. (/frontend/src/components/QuestionView)
                        'categories': {c.id:c.type for c in Category.query.all()},
                        # Here we pass None, as this value would be filled by the function in QuestionView
                        'current_category': None
                        
                        })

    @app.route('/questions/<int:question_id>', methods=['GET'])
    def get_question_id(question_id): # THis is a GET for question if
        question = Question.query.get(question_id)
        if question:
            return jsonify({'success': True,
                            'question': question.format()})
        return abort(404)

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
  
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            db.session.delete(question)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            # print(e.__dict__)
            return abort(404)

        finally:
            db.session.close()

        return jsonify({'success': True,
                        'question_id': question_id,
                        'message': 'Successfully deleted'
                        })

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
  
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def add_question():
        data = request.get_json()

        try:
            new_question = Question(question=data.get('question'),
                                    answer= data.get('answer'),
                                    difficulty=data.get('difficulty'),
                                    category=data.get('category'))

            db.session.add(new_question)
            db.session.commit()
        except (KeyError, SQLAlchemyError):
            print(sys.exc_info())
            return abort(422)
        finally:
            db.session.close()

        return jsonify({'success': True,
                        'message': 'Question has been added successfully to the database'})

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
  
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    @app.route('/submitSearch', methods=['POST'])
    def search_question():

        data = request.get_json()  # In the the QuestionView, the data is converted to a json
        search_term = data['searchTerm']

        # Get all the questions related to the the
        search_questions = Question.query.filter(Question.question.ilike(r'%{0}%'.format(search_term))).all()
        current_questions = paginate_questions(request, search_questions)

        return jsonify({'success': True, 'questions': current_questions, 'total_questions': len(search_questions),
                        'current_category': None})

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 
  
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):

        questions = Question.query.filter_by(category=category_id).all()
        data = [q.format() for q in questions]
        return jsonify({'success': True, 'questions': data, 'total_questions': len(questions),
                        'current_category': None})


    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
  
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        data = request.get_json()
        quiz_category = data.get('quiz_category')['id']
        # Previous question is a list
        previous_questions = data.get('previous_questions')

        if quiz_category != 0: # Basically 0 is for all categories
            # Remove the questions that are in the previous list and then pick a random question
            questions_category = Question.query.filter_by(category=quiz_category).filter(
                Question.id.notin_(previous_questions)).all()
            # print(questions_category, previous_questions)
        else:
            # use all categories
            questions_category = Question.query.filter(Question.id.notin_(previous_questions)).all()

        # Generate a random number between 0 and len(questions) from the category
        if questions_category: # Means it not empty
            rnd_nbr = random.randint(0, len(questions_category)-1)
            random_question = questions_category[rnd_nbr]
            # format the random question
            random_question = random_question.format()
        else:
            random_question = None

        return jsonify({'success':True, 'question': random_question})

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''

    @app.errorhandler(404)
    def not_found():
        error_data = {
            "success": False,
            "error": 404,
            "message": "Resource not available"
        }
        return jsonify(error_data)

    @app.errorhandler(422)
    def not_processed():
        error_data = {
            "success": False,
            "error": 422,
            "message": "Cannot be processed"
        }
        return jsonify(error_data)

    return app
