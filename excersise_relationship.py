from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# Set the configuration of the flask app
app_relation = Flask(__name__)

app_relation.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app_relation.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bb4341@localhost:5432/dmv'

# Link the db to the app
db = SQLAlchemy(app_relation)


# Create the drivers model
class Drivers(db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    state = db.Column(db.String(), nullable=False)
    issued = db.Column(db.String(), nullable=False)
    vehicles = db.relationship('Vehicles', backref='drivers', lazy=True)

    # Define the dunder wrapper method
    def __repr__(self):
        return f'<id:{self.id}, Name:{self.name}, State:{self.State}, year:{self.issued}>'


# Create the  table  model
class Vehicles(db.Model):
    __tablename__ = 'vehicles'
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(), nullable=False)
    model = db.Column(db.String(), nullable=True)
    year = db.Column(db.Integer, nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)

    # Define the dunder wrapper method
    def __repr__(self):
        return f'<id:{self.id}, Make:{self.make}, model:{self.model}, year:{self.year}>'

# Create the tables
db.create_all()

@app_relation.route('/')
def test_relationship():
    first_driver = Drivers.query.first()
    return render_template('index.html', data=first_driver)
    # return 'Hello world !'


if __name__ == '__main__':
    app_relation.run(debug=True)






