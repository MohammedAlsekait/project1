#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from models import *
import re
# TODO: connect to a local postgresql database



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  temp= Venue.query.filter_by(city=Venue.city,state=Venue.state).distinct(Venue.city,Venue.state)
  data=[]
  ven_data=[]
  num=0
  d1={}
  d2={}
  for a in temp:
    area=Venue.query.filter_by(city=a.city,state=a.state).all()
    for b in area:
      num=len(Show.query.filter(Show.start_time > datetime.now()).all())
      d1={
        "id": b.id,
        "name": b.name,
        "num_upcoming_shows": num,
      }
      ven_data.append(d1)
    d2={
      "city": a.city,
      "state": a.state,
      "venues":ven_data
    }
    data.append(d2)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term=request.form.get('search_term',)
  res=Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  num=len(Show.query.filter(Show.start_time > datetime.now()).all())
  list=[]
  dic={}
  count=0
  for a in res:
    count+=1
    dic={
      "id": a.id,
      "name": a.name,
      "num_upcoming_shows": num
    }
    list.append(dic)
  response={
    "count": count,
    "data": list
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data=[]
  ven=Venue.query.get(venue_id)
  sh=Show.query.join(Venue).filter(venue_id==Show.venue_id).all()
  ps=[]
  ucs=[]
  count_ps=0
  count_ucs=0
  for a in sh:
    if a.start_time > datetime.now():
      count_ucs+=1
      temp = {
        "artist_id": a.artist_id,
        "artist_name": Artist.query.get(a.artist_id).name,
        "artist_image_link": Artist.query.get(a.artist_id).image_link,
        "start_time": format_datetime(str(a.start_time))
      }
      ucs.append(temp)
    else:
      count_ps+=1
      temp={
        "artist_id": a.artist_id,
        "artist_name": Artist.query.get(a.artist_id).name,
        "artist_image_link": Artist.query.get(a.artist_id).image_link,
        "start_time": format_datetime(str(a.start_time))
     }
      ps.append(temp)
  data={
    "id": ven.id,
    "name": ven.name,
    "genres": [ven.genres],
    "address": ven.address,
    "city": ven.city,
    "state": ven.state,
    "phone": ven.phone,
    "website": ven.website,
    "facebook_link": ven.facebook_link,
    "seeking_talent": ven.seeking_talent,
    "seeking_description":ven.seeking_description ,
    "image_link": ven.image_link,
    "past_shows":ps,
    "upcoming_shows": ucs,
    "past_shows_count": count_ps,
    "upcoming_shows_count": count_ucs,
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  fm = VenueForm()
  error=False
  str=''
  try:
    name=fm.name.data.strip()
    city = fm.city.data.strip()
    state = fm.state.data.strip()
    address = fm.address.data.strip()
    phone = fm.phone.data
    if re.match(r"^[\+\(]?\d+(?:[- \)\(]+\d+)+$", phone):#check for the validation of the number
      pass
    else:
      str='invalid phone number'
      raise UnboundLocalError()
    image_link = fm.image_link.data.strip()
    facebook_link = fm.facebook_link.data.strip()
    website = fm.website_link.data.strip()
    seeking_talent = fm.seeking_talent.data
    seeking_description = request.form['seeking_description']
    genres = fm.genres.data
    if fm.validate():
      flash(fm.errors)
      return

    ven=Venue(name=name,city=city,state=state,address=address,phone=phone,
              image_link=image_link,facebook_link=facebook_link,website=website,
              seeking_talent=seeking_talent,seeking_description=seeking_description,
              genres=genres)
    db.session.add(ven)
    str = 'e'
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error==True:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed. '+str)
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  error = False
  try:
    ven = Venue.query.get(venue_id)
    name=ven.name
    db.session.delete(ven)
    db.session.commit()
  except():
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error == True:
    flash('An error occurred. Venue ' + name + ' could not be listed.')
  else:
    flash('Venue ' + name + ' was successfully listed!')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  ars=Artist.query.all()
  temp = {}
  data=[]
  for a in ars:
    temp={
      "id": a.id,
      "name": a.name,
    }
    data.append(temp)

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', )
  res = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  count=0
  dic={}
  data=[]
  #num_upcoming_shows=Show.query.filter(Show.artist_id==res.id).filter(Show.start_time>datetime.now()).all()
  for ars in res:
    count+=1
    dic={
      "id": ars.id,
      "name": ars.name,
      "num_upcoming_shows": 0,
    }
    data.append(dic)

  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  ars = Artist.query.get(artist_id)
  shw=Show.query.join(Artist).filter(artist_id==Show.artist_id).all()
  count_ucs=0
  count_ps=0
  ucs=[]
  ps=[]
  for a in shw:
    if a.start_time > datetime.now():
      count_ucs+=1
      temp = {
        "venue_id": a.artist_id,
        "venue_name": Venue.query.get(a.venue_id).name,
        "venue_image_link": Venue.query.get(a.venue_id).image_link,
        "start_time": format_datetime(str(a.start_time))
      }
      ucs.append(temp)
    else:
      count_ps+=1
      temp={
      "venue_id": a.venue_id,
      "venue_name": Venue.query.get(a.venue_id).name,
      "venue_image_link": Venue.query.get(a.venue_id).image_link,
      "start_time": format_datetime(str(a.start_time))
     }
      ps.append(temp)

  data={
    "id": ars.id,
    "name": ars.name,
    "genres": [ars.genres],
    "city": ars.city,
    "state": ars.state,
    "phone": ars.phone,
    "website": ars.website,
    "facebook_link": ars.facebook_link,
    "seeking_venue": ars.seeking_venue,
    "seeking_description":ars.seeking_description ,
    "image_link": ars.image_link,
    "past_shows": ps,
    "upcoming_shows": ucs,
    "past_shows_count": count_ps,
    "upcoming_shows_count": count_ucs,
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  ars=Artist.query.get(artist_id)
  artist={
    "id": ars.id,
    "name": ars.name,
    "genres": [ars.genres],
    "city": ars.city,
    "state": ars.state,
    "phone": ars.phone,
    "website": ars.website,
    "facebook_link": ars.facebook_link,
    "seeking_venue": ars.seeking_venue,
    "seeking_description":ars.seeking_description ,
    "image_link": ars.image_link,
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  ars=Artist.query.get(artist_id)
  error=False

  try:
    ars.name=request.form['name']
    ars.city=request.form['city']
    ars.state=request.form['state']
    ars.image_link=request.form['image_link']
    ars.facebook_link=request.form['facebook_link']
    ars.phone=request.form['phone']
    ars.genres=request.form.getlist('genres')
    ars.seeking_description=request.form['seeking_description']
    ars.seeking_venue=True if 'seeking_venue' in request.form else False
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error == True:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully edited!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  ven=Venue.query.get(venue_id)
  venue={
    "id": ven.id,
    "name": ven.name,
    "genres": [ven.genres],
    "address": ven.address,
    "city": ven.city,
    "state": ven.state,
    "phone": ven.phone,
    "website": ven.website,
    "facebook_link": ven.facebook_link,
    "seeking_talent": ven.seeking_talent,
    "seeking_description": ven.seeking_description,
    "image_link": ven.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  ven=Venue.query.get(venue_id)
  error=False
  try:
    ven.name=request.form['name']
    ven.city = request.form['city']
    ven.state = request.form['state']
    ven.address = request.form['address']
    ven.phone = request.form['phone']
    ven.image_link = request.form['image_link']
    ven.facebook_link =request.form['facebook_link']
    ven.seeking_talent = True if 'seeking_talent' in request.form else False
    ven.seeking_description = request.form['seeking_description']
    ven.genres = request.form.getlist('genres')
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error == True:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
  else:
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  fm=ArtistForm()
  str=''
  error = False
  try:
    name = fm.name.data.strip()
    city = fm.city.data.strip()
    state = fm.state.data.strip()
    phone = fm.phone.data
    if re.match(r"^[\+\(]?\d+(?:[- \)\(]+\d+)+$", phone):  # check for the validation of the number
      pass
    else:
      str = 'invalid phone number'
      raise UnboundLocalError()
    website = fm.website_link.data.strip()
    image_link = fm.image_link.data.strip()
    facebook_link = fm.facebook_link.data.strip()
    seeking_venue = fm.seeking_venue.data
    seeking_description = request.form['seeking_description']
    genres = fm.genres.data
    if fm.validate():
      flash(fm.errors)
      return
    ars = Artist(name=name, city=city, state=state, phone=phone,website=website,
                image_link=image_link, facebook_link=facebook_link,
                seeking_venue=seeking_venue, seeking_description=seeking_description,
                genres=genres)
    db.session.add(ars)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error == True:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.'+str)
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shw=Show.query.all()
  data=[]
  for s in shw:
    dic = {
      "venue_id": s.venue_id,
      "venue_name": s.venue.name,
      "artist_id": s.artist_id,
      "artist_name": s.artist.name,
      "artist_image_link":s.artist.image_link ,
      "start_time": format_datetime(str(s.start_time))
    }
    data.append(dic)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  str='Check the IDs it can be found on the Artists & Venues Pages'
  fm=ShowForm()
  error = False
  try:
    ven_id=fm.venue_id.data
    ars_id=fm.artist_id.data
    start_t=fm.start_time.data

    if fm.validate():
      flash(fm.errors)
      return
    shw=Show(venue_id=ven_id,artist_id=ars_id,start_time=start_t)
    db.session.add(shw)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error == True:
    flash('Show faild to be listed! '+str)
  else:
    flash('Show was successfully listed!')

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
