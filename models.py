#Import libraries
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_migrate import Migrate
from datetime import datetime



#Configure app

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

#Set the model 

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#




class Venue(db.Model):
    __tablename__ = 'Venue'


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    image_link = db.Column(db.String(500))
    seeking_description = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean, default=False)
    shows = db.relationship('Show', backref='Venue', lazy='dynamic')
    # TODO: End

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    seeking_description = db.Column(db.String)
    image_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Artist', lazy='dynamic')

    # TODO End

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration./
class Show(db.Model):

    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)

    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

    start_time = db.Column(db.DateTime(timezone=True))


