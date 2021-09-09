from flask import Flask
from flask_migrate import Migrate
import config
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),unique=True,nullable=False)
    phone = db.Column(db.String(120),unique=True,nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120),unique=True,nullable=False)
    shows=db.relationship('Show',backref= 'venue',lazy=True)
    website=db.Column(db.String(),unique=True,nullable=False)
    seeking_talent=db.Column(db.Boolean,default=False)
    seeking_description=db.Column(db.String())
    genres=db.Column(db.ARRAY(db.String()),nullable=False)

    def __repr__(self):
      return f'<venues {self.id} {self.name}>'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),unique=True,nullable=False)
    genres = db.Column(db.String(120),nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120),unique=True,nullable=False)
    shows = db.relationship('Show', backref='artist', lazy=True)
    website=db.Column(db.String(),unique=True,nullable=False)
    seeking_venue=db.Column(db.Boolean,default=False)
    seeking_description=db.Column(db.String())

    def __repr__(self):
      return f'<artists {self.id} {self.name}>'


class Show(db.Model):
  __tablename__ = 'shows'
  id=db.Column(db.Integer,primary_key=True)
  venue_id=db.Column(db.Integer,db.ForeignKey('venues.id'),nullable=False)
  artist_id=db.Column(db.ForeignKey('artists.id'),nullable=False)
  start_time=db.Column(db.DateTime,nullable=False)
  def __repr__(self):
        return f'<Show {self.id} {self.artist_id} {self.venue_id}>'
