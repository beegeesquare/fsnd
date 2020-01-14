from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

# Set the configuration of the flask app
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bb4341@localhost:5432/example'

# Link the instance of the database to the flask app
db = SQLAlchemy(app)

# postgresql://myusername:mypassword@localhost:5432/mydatabase
# Optionally we can add the DBAPI that the database supports. For python the default is psycopg2
# postgresql+psycopg2://myusername:mypassword@localhost:5432/mydatabase
# dialect://username:password@host:port/dbname

# Create a new table in the database 'example'
class Person(db.Model):
    # No need to specify the __init__ method here; SQLAlchemy does that for us
    __tablename__ = 'persons'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'<Person ID: {self.id}, Last name: {self.last_name}, First name: {self.first_name}>'

# We need to create the table in the db; if the table already exists, nothing happens
db.create_all()


@app.route('/')
def index():
    person = Person.query.first() # Gives the first entry in the database
    return 'Hello world ! ' + person.first_name + ' ' + person.last_name


if __name__ == '__main__':
    app.run(debug=True)



