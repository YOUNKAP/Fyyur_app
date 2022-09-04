#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from datetime import datetime
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
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
    # Set the current date
    current_date = datetime.now()
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



@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id=venue_id).all()
  past_shows = []
  upcoming_shows = []
  current_time = datetime.now()

  for show in shows:
    data = {
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
           "artist_image_link": show.artist.image_link,
           "start_time": format_datetime(str(show.start_time))
        }
    if show.start_time > current_time:
      upcoming_shows.append(data)
    else:
      past_shows.append(data)
 
  keys = [    
    "id",
    "name",
    "genres",
    "address",
    "city",
    "state",
    "phone",
    "website",
    "facebook_link",
    "seeking_talent",
    "seeking_description",
    "image_link",
    "past_shows",
    "upcoming_shows",
    "past_shows_count",
    "upcoming_shows_count"
    ]

  values =  [
    venue.id,
    venue.name,
    venue.genres,
    venue.address,
    venue.city,
    venue.state,
    venue.phone,
    venue.website,
    venue.facebook_link,
    venue.seeking_talent,
    venue.seeking_description,
    venue.image_link,
    past_shows,
    upcoming_shows,
    len(past_shows),
    len(upcoming_shows)
                      ]


  data = dict(zip(keys, values ))
 
  
  ###________________________________________________________________________### 
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

  try:
    # get form data and create 
    form = VenueForm()
    #Set venue
    venue = Venue(name=form.name.data, 
                  city=form.city.data, 
                  state=form.state.data, 
                  address=form.address.data,
                  phone=form.phone.data, 
                  image_link=form.image_link.data,
                  genres=form.genres.data, 
                  facebook_link=form.facebook_link.data, 
                  seeking_description=form.seeking_description.data,
                  website=form.website.data, 
                  seeking_talent=form.seeking_talent.data)
    
    # Add venue
    db.session.add(venue)
    #Commit to database
    db.session.commit()

    # flash success 
    flash('Awesome the venue : ' + request.form['name'] + ' is listed.')
  except:
    # catch error
    db.session.rollback()
    flash('Sorry an error occurred. the venue ' + request.form['name'] + ' not found !')
  finally:
    # closes session
    db.session.close()
  ###________________________________________________________________________### 
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
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
  except:
    flash('an error occured and Venue ' + venue_name + ' was not deleted')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('index'))

  ###________________________________________________________________________### 
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
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id=artist_id).all()
  past_shows = list()

  upcoming_shows = list()

  current_time = datetime.now()

  # Filter shows by upcoming and past
  for show in shows:
    data = {"venue_id": show.venue_id, "venue_name": show.venue.name, "venue_image_link": show.venue.image_link, "start_time": format_datetime(str(show.start_time))}

    if show.start_time > current_time:

      upcoming_shows.append(data)

    else:
      past_shows.append(data)

  values =[
    artist.id,
    artist.name,
    artist.genres,
    artist.city,
    artist.state,
    artist.phone,
    artist.facebook_link,
    artist.image_link,
    past_shows,
    upcoming_shows,
    len(past_shows),
   len(upcoming_shows)
  ]

  keys =[
    "id",
    "name",
    "genres",
    "city",
    "state",
    "phone",
    "facebook_link",
    "image_link",
    "past_shows",
    "upcoming_shows",
    "past_shows_count",
    "upcoming_shows_count"
  ]

  data = dict(zip(keys, values))
  ###________________________________________________________________________### 
  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------

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
  try:
    form = ArtistForm()
    #Select artist by ID
    artist = Artist.query.get(artist_id)
    #Get artist name
    artist.name = form.name.data
    #Get artist Phone number
    artist.phone = form.phone.data
    #Get artist state
    artist.state = form.state.data
    #Get artist city
    artist.city = form.city.data
    #Get artistes genre
    artist.genres = form.genres.data
    #Get artist image link
    artist.image_link = form.image_link.data
    #Get artist facebook link
    artist.facebook_link = form.facebook_link.data
    #commit the session
    db.session.commit()

    flash('Awesome artist ' + request.form['name'] + ' is updated!')
  except:
    db.session.rolback()
    flash('Sorry, unsuccesfull update')
  finally:
    db.session.close()
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
    "website",
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
    venue.website,
    venue.facebook_link,
    venue.seeking_talent,
    venue.seeking_description,
    venue.image_link,
   ]
  venue = dict(zip(venue_keys, venue_values))
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    form = VenueForm()
    #Select venue by ID
    venue = Venue.query.get(venue_id)
    #Get venue name
    name = form.name.data
    #Get venue genres
    venue.genres = form.genres.data
    #Get venue city
    venue.city = form.city.data
    #Get venue state
    venue.state = form.state.data
    #Get venue address
    venue.address = form.address.data
    #Get venue phone
    venue.phone = form.phone.data
    #Get venue facebook link
    venue.facebook_link = form.facebook_link.data
    #Get venue website
    venue.website = form.website.data
    #Get venue image
    venue.image_link = form.image_link.data
    #Get venue talent
    venue.seeking_talent = form.seeking_talent.data
    #Get venue description
    venue.seeking_description = form.seeking_description.data
    #Commit to database
    db.session.commit()
    flash('Awesome the venue ' + name + '  updated')
  except:
    db.session.rollback()
    flash('Sorry an error occur when trying to update venue')
  finally:
    db.session.close()

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
  try:
    form = ArtistForm()

    artist = Artist(name=form.name.data, city=form.city.data, state=form.city.data,
                    phone=form.phone.data, genres=form.genres.data, 
                    image_link=form.image_link.data, facebook_link=form.facebook_link.data)
    
    db.session.add(artist)
    db.session.commit()

    flash('Awesome the Artist : ' + request.form['name'] + ' is  listed!')
  except:
    db.session.rollback()
    flash('Sorry an error occurs ' + request.form['name'] + ' could not be listed !')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/artist/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:

    artist = Artist.query.get(artist_id)
    artist_name = artist.name

    db.session.delete(artist)
    db.session.commit()

    flash('The Artist ' + artist_name + ' was successfully  deleted')
  except:
    flash('Sorry an error occurs the Artist : ' + artist_name + ' is not deleted')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('index'))



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.order_by(db.desc(Show.start_time))

  data = list()

  for show in shows:

    data_dict = {
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": format_datetime(str(show.start_time))
        }
    data_keys = [
        "venue_id",
        "venue_name",
        "artist_id",
        "artist_name",
        "artist_image_link",
        "start_time"
        ]

    data_values = [
       show.venue_id,
       show.venue.name,
       show.artist_id,
       show.artist.name,
       show.artist.image_link,
      format_datetime(str(show.start_time))
    ]

    data_dict  = dict(zip(data_keys, data_keys))

    data.append(data_dict)

  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)
  

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    show = Show(artist_id=request.form['artist_id'], venue_id=request.form['venue_id'], start_time=request.form['start_time'])

    db.session.add(show)
    db.session.commit()

    flash('Awesome Show Successfully listed!')
  except:
    db.session.rollback()
    flash('Sorry Show could not be listed.')
  finally:
    db.session.close()

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
