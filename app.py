#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
#from flask_wtf import FlaskForm as Form
import dateutil.parser
import babel
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from datetime import datetime, timezone
from flask_migrate import Migrate
import sys
from sqlalchemy import or_, desc
from forms import *
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# TODO: connect to a local postgresql database
#SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:eddy@localhost:5432/fyyur'
###________________________________________________________________________###

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
  #num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = list()
  # Select all venues
  venues = Venue.query.all()
  locations = list()
  for venue in venues:
    if venue not in locations :
      locations.append((venue.city, venue.state))
  for loc in locations:
    data.append({
        "city": loc[0],
        "state": loc[1],
        "venues": []
    })


  for venue in venues:
    num_upcoming_shows = 0
    #Select shwos
    shows = Show.query.filter_by(venue_id=venue.id).all()
    #current_date = datetime.now()
    current_date = datetime.now(timezone.utc)
    for show in shows:
      if show.start_time >= current_date:
          num_upcoming_shows += 1

    for location in data:

      if venue.state == location['state'] and venue.city == location['city']:

        location['venues'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming_shows
        })
  ###________________________________________________________________________###     
  return render_template('pages/venues.html', areas=data)






@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term', '')

  result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))

  response={

    "count": result.count(),
    
    "data": result
  }
  ###________________________________________________________________________### 
  return render_template('pages/search_venues.html', results=response, search_term=search_term)


#################Good here ###############################################################

@app.route('/venues/<int:venue_id>')

def show_venue(venue_id):

  #venue = db.session.query(Venue).filter(Venue.id == venue_id).all()
  venue = Venue.query.get(venue_id)

  data = dict()

  past_shows = list()

  upcoming_shows = list()


  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==Artist.id).filter(Show.start_time<datetime.now()).all()  


  for show in past_shows_query:



    artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()

    artist_data= {
                  "artist_id": show.artist_id,
                  "artist_name": artist.name,
                  "artist_image_link": artist.image_link,
                  "start_time": show.start_time.strftime('%m/%d/%Y'),
                  }

    past_shows.append(artist_data)


  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==Artist.id).filter(Show. start_time>datetime.now()).all()

  for show in upcoming_shows_query:

    artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()

    artist_data = {
                  "artist_id": show.artist_id,
                  "artist_name": artist.name,
                  "artist_image_link": artist.image_link,
                  "start_time": show.start_time.strftime('%m/%d/%Y'),
                  }

    upcoming_shows.append(artist_data)

  venue_data_keys = [

    "id",
    "name",
    "genres",
    "address",
    "city",
    "state",
    "phone",
    "website_link",
    "facebook_link",
    "seeking_talent",
    "seeking_description",
    "image_link",
    "past_shows",
    "upcoming_shows",
    "past_shows_count",
    "upcoming_shows_count"]


  venue_data_values  =[

    venue.id,
    venue.name,
    venue.genres,
    venue.address,
    venue.city,
    venue.state,
    venue.phone,
    venue.website_link,
    venue.facebook_link,
    venue.seeking_talent,
    venue.seeking_description,
    venue.image_link,
    past_shows,
    upcoming_shows,
    len(past_shows),
    len(upcoming_shows)]

  data =   dict(zip(venue_data_keys,    venue_data_values ))

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

  # Set the FlaskForm
  form = VenueForm(request.form, meta={'csrf': False})

  # Validate all fields

  if form.validate():

    try:

      venue = Venue(name=form.name.data,  
                  city=form.city.data, 
                  state=form.state.data,  
                  address=form.address.data,
                  phone=form.phone.data, 
                  image_link=form.image_link.data,
                  genres=form.genres.data, 
                  facebook_link=form.facebook_link.data, 
                  seeking_description=form.seeking_description.data,
                  website_link=form.website_link.data, 
                  seeking_talent= form.seeking_talent.data)
      #Add to database
      db.session.add(venue)
      db.session.commit()

      # flash success 
      flash('Awesome the venue : ' + form.name.data + ' is listed.')
    except ValueError as e :
      print(e)
      # catch error
      db.session.rollback()
      flash('Sorry an error occurred. the venue ' + form.name.data + ' not found !')
    finally:
      # closes session
      db.session.close()
  
  # If there is any invalid field
  else:
    message = []
    for field, err in form.errors.items():

      message.append(field + ' ' + '|'.join(err))
    
    flash('Errors ' + str(message))


  ###________________________________________________________________________### 
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    # Get venue by ID
    venue = Venue.query.get(venue_id)
    venue_name = venue.name

    db.session.delete(venue)
    db.session.commit()

    flash('Venue ' + venue_name + ' was deleted')
  except ValueError as e :
    print(e)
    flash('an error occured and Venue ' + venue_name + ' was not deleted')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = list()
  #Select all artists
  artists = Artist.query.all()

  for artist in artists:
    artist_data = { "id": artist.id,"name": artist.name}
    data.append(artist_data)
  ###________________________________________________________________________### 
  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')

  # filter artists 
  result = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
  response={"count": result.count(), "data": result }
  ###________________________________________________________________________### 
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #Query Artist by ID
  artists = db.session.query(Artist).filter(Artist.id == artist_id).all()
  #Get the current time
  current_time = datetime.now(timezone.utc)
  data= dict()
  down_show = list()
  up_show = list()

  for artist in artists :
        artist_data_keys = ["id", "name", "genres", "city", "state","phone", "website_link","facebook_link",
                           "seeking_venue", "seeking_description", "image_link" ]
        artist_data_values = [ artist.id, artist.name, artist.genres.split(", "), artist.city,
                               artist.state, artist.phone, artist.website_link, artist.facebook_link,
                               artist.seeking_venue, artist.seeking_description, artist.image_link]

        data_artist = dict(zip(artist_data_keys,  artist_data_values))

        data.update(data_artist)
        #Get upcomming shows
        upcoming_shows = artist.shows.filter(Show.start_time > current_time).all()
        for show in upcoming_shows:
            if len(upcoming_shows) == 0:
                  data.update({"upcoming_shows": [],})
            else:
                  venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id == show.venue_id).one()
                  
                  venue_data_keys = ["venue_id","venue_name","venue_image_link","start_time"]

                  venue_data_values = [show.venue_id,  venue.name ,venue.image_link, show.start_time.strftime('%m/%d/%Y')]

                  venue_data =  dict(zip(venue_data_keys,  venue_data_values))

                  up_show.append(venue_data)

        #Get pass swow
        past_shows = artist.shows.filter(Show.start_time < current_time).all()
        for show in past_shows:
            if len(past_shows) == 0:
                  data.update({"past_shows": [],})
            else:
                  venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id == show.venue_id).one()

                  venue_data_keys = ["venue_id","venue_name","venue_image_link","start_time"]

                  venue_data_values = [show.venue_id,  venue.name ,venue.image_link, show.start_time.strftime('%m/%d/%Y')]

                  venue_data =  dict(zip(venue_data_keys,  venue_data_values))

                  down_show.append(venue_data)

        #Update Upcoming shows
        data.update({"upcoming_shows": up_show})
        #Update Past shows
        data.update({"past_shows": down_show})
        data.update({"past_shows_count": len(past_shows), "upcoming_shows_count": len(upcoming_shows),})
  #End TODO
  return render_template('pages/show_artist.html', artist=data)



@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
#TODO
def edit_artist(artist_id):

  form = ArtistForm()
  #Select artist by id
  artist = Artist.query.get(artist_id)

  artist_data_keys = [
        "id",
        "name",
        "genres",
        "city",
        "state",
        "phone",
        "facebook_link",
        "image_link"
  ]

  artist_data_values = [
     artist.id,
        artist.name,
        artist.genres,
        artist.city,
        artist.state,
        artist.phone,
        artist.facebook_link,
        artist.image_link
  ]

  artist_data = dict(zip(artist_data_keys,  artist_data_values))

  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form, meta={"csrf": False})
  artist = Artist.query.get(artist_id)
  if form.validate():
    try:
      #Get artist name
      artist.name = form.name.data
      artist.city = form.city.data
      artist.genres = form.genres.data
      artist.state =form.state.data
      artist.phone = form.phone.data
      artist.website_link = form.website_link.data
      artist.facebook_link =form.facebook_link.data
      artist.image_link =form.image_link.data
      artist.seeking_venue =form.seeking_venue.data
      artist.seeking_description =form.seeking_description.data 
      """
      artist = Artist(
            name=form.name.data,
            city=form.city.data,
            genres = form.genres.data,
            state = form.state.data,
            phone = form.phone.data,
            website_link = form.website_link.data,
            facebook_link = form.facebook_link.data,
            image_link = form.image_link.data,
            seeking_venue = form.seeking_venue.data,
            seeking_description =form.seeking_description.data
            ) 
      """
      db.session.add(artist)
      #Commit the data base
      db.session.commit()
      flash('Awesome artist ' + form.name.data + ' is updated!')
    except:
      db.session.rollback()
      flash('Sorry, unsuccesfull update')
    finally:
      db.session.close()
  # If there is any invalid field
  else:
    message = []
    for field, err in form.errors.items():

      message.append(field + ' ' + '|'.join(err))
    
    flash('Errors ' + str(message)) 
  return redirect(url_for('show_artist', artist_id=artist_id))



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
# TODO: populate form with values from venue with ID <venue_id>
def edit_venue(venue_id):
  form = VenueForm()
  #Select venue by id
  venue = Venue.query.get(venue_id)
  venue_keys=[
    "id",
    "name",
    "genres",
    "address",
    "city",
    "state",
    "phone",
    "website_link",
    "facebook_link",
    "seeking_talent",
    "seeking_description",
    "image_link",
    ]

  venue_values = [
    venue.id,
    venue.name,
    venue.genres,
    venue.address,
    venue.city,
    venue.state,
    venue.phone,
    venue.website_link,
    venue.facebook_link,
    venue.seeking_talent,
    venue.seeking_description,
    venue.image_link,
   ]
  venue = dict(zip(venue_keys, venue_values))
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

    # Set the FlaskForm
  form = VenueForm(request.form, meta={'csrf': False})
  venue = Venue.query.get(venue_id)

  # Validate all fields

  if form.validate():

    try:
      #Select Venue by ID
      venue = Venue(name=form.name.data,  
                  city=form.city.data, 
                  state=form.state.data,  
                  address=form.address.data,
                  phone=form.phone.data, 
                  image_link=form.image_link.data,
                  genres=form.genres.data, 
                  facebook_link=form.facebook_link.data, 
                  seeking_description=form.seeking_description.data,
                  website_link=form.website_link.data, 
                  seeking_talent= form.seeking_talent.data)
      #Add to database
      db.session.add(venue)
      db.session.commit()

      flash('Awesome the venue ' + venue.name  + '  updated')
    except:
      db.session.rollback()
      flash('Sorry an error occur when trying to update venue')
    finally:
      db.session.close()
  # If there is any invalid field
  else:
    message = []
    for field, err in form.errors.items():

      message.append(field + ' ' + '|'.join(err))
    
    flash('Errors ' + str(message))

  #End TODO
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
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form, meta={"csrf": False})
  if form.validate():
    try:
      artist = Artist() 
      artist.name = form.name.data
      artist.city = form.city.data
      artist.genres = form.genres.data
      artist.state =form.state.data
      artist.phone = form.phone.data
      artist.website_link = form.website_link.data
      artist.facebook_link =form.facebook_link.data
      artist.image_link =form.image_link.data
      artist.seeking_venue =form.seeking_venue.data
      artist.seeking_description =form.seeking_description.data 
      """
      artist = Artist(
            name=form.name.data,
            city=form.city.data,
            genres = form.genres.data,
            state = form.state.data,
            phone = form.phone.data,
            website_link = form.website_link.data,
            facebook_link = form.facebook_link.data,
            image_link = form.image_link.data,
            seeking_venue = form.seeking_venue.data,
            seeking_description =form.seeking_description.data
            ) 
      """
      db.session.add(artist)
      #Commit the data base
      db.session.commit()
      flash('Awesome artist ' + form.name.data + ' is updated!')
    except ValueError as e:
      print(e)
      db.session.rollback()
      flash('Sorry, unsuccesfull update')
    finally:
      db.session.close()
  # If there is any invalid field
  else:
    message = []
    for field, err in form.errors.items():

      message.append(field + ' ' + '|'.join(err))
    
    flash('Errors ' + str(message)) 
  return render_template('pages/home.html')


@app.route('/artists/<artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a artist_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    #Query show by artist ID 
    show = Show.query.filter_by(artist_id=artist_id)
    show.delete()
    #Query artist info by ID 
    artist = Artist.query.filter_by(id=artist_id)
    artist.delete()
    #Commit to database
    db.session.commit()
    flash('Wel done,  Artist succesfully delete')
  except:
    flash('Error,  Unable to delete artist from database')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')


@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = list()
  #Query show by start time
  shows = db.session.query(Show).order_by(desc(Show.start_time)).all()

  for show in shows:

        artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()

        venue = db.session.query(Venue.name).filter(Venue.id == show.venue_id).one()  

        artist_data_keys =[
          "artist_id",
          "artist_name",
          "artist_image_link",
          "start_time",
          "venue_id",
          "venue_name"
        ]

        artist_data_values = [
               show.artist_id,
              artist.name,
              artist.image_link,
              format_datetime(str(show.start_time)),
               show.venue_id,
               venue.name
        ]

        artist_data = dict(zip(artist_data_keys, artist_data_values))

        data.append(artist_data)

  #End TODO
  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])

def create_show_submission():

  form = ShowForm(request.form, meta={"csrf": False})

  if form.validate():

    try:

      show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=form.start_time.data
        )
      db.session.add(show)
      db.session.commit()
    except ValueError as e:
      print(e)
      db.session.rollback()

      flash('Sorry Show could not be listed.')

    finally:

      db.session.close()
  else:
    message = []
    for field, err in form.errors.items():

      message.append(field + ' ' + '|'.join(err))
    
    flash('Errors ' + str(message)) 

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

