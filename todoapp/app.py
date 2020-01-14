from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# Create an application based on the name of the app
app = Flask(__name__)

# Link to the app to the postgresql database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Note that for creating the database, we need to run the createdb on the CLI
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bb4341@localhost:5432/tododb'

# Start linking the database to the app
db = SQLAlchemy(app)  # Put the name of the app here

# Now create a class that would inheret the db
class Todo(db.Model):
    __tablename__ = 'todos' # If the table name is not given then the name of the table is the class name (ignoring case)
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)

    # Define a dunder wrapper method for printing the rows in the table
    def __repr__(self):
        return f'<Todo: {self.id} {self.description}>'

# Create all the models that were defined
db.create_all()


@app.route('/')
def index():
    return render_template('index.html', data=Todo.query.all())
    #return render_template('index.html', data=[{'description': 'Todo 1'},
    #                                    {'description': 'Todo 2'},
    #                                    {'description': 'Todo 3'}
    #                                    ]
    #                )
