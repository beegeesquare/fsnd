from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.sql import expression
import sys
from flask_migrate import Migrate


# Create an application based on the name of the app
app = Flask(__name__)

# Link to the app to the postgresql database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Note that for creating the database, we need to run the createdb on the CLI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bb4341@localhost:5432/tododb'

# Start linking the database to the app
db = SQLAlchemy(app)  # Put the name of the app here

# Create a migrate class
migrate = Migrate(app, db) # Pass the name of the app to the migrate


# Now create a class that would inheret the db
class Todo(db.Model):
    __tablename__ = 'todos' # If the table name is not given then the name of the table is the class name (ignoring case)
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    # Completed need not be set to any nullable value
    completed = db.Column(db.Boolean, nullable=False, default=False)
    # Here for now the nullable is set True, so we can run the migration
    # This needs to be changed later
    # Change the nullable constraint to False  after updating the table in the psql
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    # Define a dunder wrapper method for printing the rows in the table
    def __repr__(self):
        return f'<Todo: {self.id} {self.description}>'


# Create a todolist
class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    # Define the relationship with todos
    todos = db.relationship('Todo', backref='todolists', lazy=True)

# Create all the models that were defined
# We won't be using in the migration model
# db.create_all()


@app.route('/todos/create', methods=['POST'])
def create_todo():
    # First get the description text from the name of the HTML form
    # Here "get" method gives the data in "name" type of the HTML form
    # '' (empty string) is used for default value, in case the data is missing
    # Other way of doing this is using json, 'requests.data'
    description = request.get_json()['description']
    # Using this description create a new toodo object (purposefully misspelled)

    # Add the expections
    error = False
    body = {}
    try:
        todo = Todo(description=description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        db.session.rollback()
        error = True
        print(sys.exec_info())
    finally:
        db.session.close()

    if error:
        abort(400)
    else:
        return jsonify(body)


@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        # This is id that we get from the UI and then we use that update the table
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('index'))


@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})


@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.order_by('id').all())
    #return render_template('index.html', data=[{'description': 'Todo 1'},
    #                                    {'description': 'Todo 2'},
    #                                    {'description': 'Todo 3'}
    #                                    ]
    #                )
