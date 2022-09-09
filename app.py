#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,  abort
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
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  #Get all cities 
  cities = db.session.query(Venue.city).group_by(Venue.city).all()
  #Set current time
  current_time = datetime.now(timezone.utc)

  current_city=' '

  data=list()

  for city in cities:
      #Get all venues
      venues = db.session.query(Venue).filter(Venue.city == city[0]).order_by('id').all()
      for venue in venues:
          #Get incomming showq
          num_upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()  

          if current_city != venue.city:

            venue_data ={
                "city":venue.city,
                "state":venue.state,
                "venues":[{
                "id": venue.id,
                "name":venue.name,
                "num_upcoming_shows": len(num_upcoming_shows)}]
                }

            data.append(venue_data)

            current_city=venue.city
            
          else: 
            nb_data = len(data) - 1 

            data[nb_data]["venues"].append(
              {
                "id": venue.id,
                "name":venue.name,
                "num_upcoming_shows": len(num_upcoming_shows)
              }
              )
  #End todo app

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  #Get search term
  search_term  = request.form.get('search_term')
  #Set search criteria
  search_criteria = "%{}%".format(search_term .lower())
  #Query Search resuLT
  result = Venue.query.filter(or_(Venue.name.ilike(search_criteria), Venue.city.ilike(search_criteria), Venue.state.ilike(search_criteria))).all()
  #Build the response
  response = {'count':len(result),'data':result}
  #Return the search result
  #End TODO
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #Get all venue
  venue = db.session.query(Venue).filter(Venue.id == venue_id).all()

  current_time = datetime.now(timezone.utc)

  data= dict()

  down_show = list()

  up_show = list()

  for col in venue:
        #Get upcomming shows
        upcoming_shows = col.shows.filter(Show.start_time > current_time).all()
        #Get pass show
        past_shows = col.shows.filter(Show.start_time < current_time).all()
        #Update the venue data
        venue_data = {
        "id": col.id,
        "name": col.name,
        "genres": col.genres.split(", "),
        "address": col.address,
        "city": col.city,
        "state": col.state,
        "phone": col.phone,
        "website": col.website,
        "facebook_link": col.facebook_link,
        "seeking_talent": col.seeking_talent,
        "seeking_description": col.seeking_description,
        "image_link": col.image_link,
        }
        data.update(venue_data)

        for show in upcoming_shows:

            if len(upcoming_shows) == 0:

                  data.update({"upcoming_shows": [],})

            else:
                  artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
                  artist_data = {
                  "artist_id": show.artist_id,
                  "artist_name": artist.name,
                  "artist_image_link": artist.image_link,
                  "start_time": show.start_time.strftime('%m/%d/%Y'),
                  }
                  up_show.append(artist_data)

        for show in past_shows:

            if len(past_shows) == 0:

                  data.update({"past_shows": [],})
            else:
                  #Get artist infors
                  artist = db.session.query(Artist.name, Artist.image_link).filter(Artist.id == show.artist_id).one()
                  artist_data = {
                  "artist_id": show.artist_id,
                  "artist_name": artist.name,
                  "artist_image_link": artist.image_link,
                  "start_time": show.start_time.strftime('%m/%d/%Y'),
                  }
                  down_show.append(artist_data )
        #Update upcoming Shows
        data.update({"upcoming_shows": up_show})
        #Update past Shows
        data.update({"past_shows": down_show})

        data.update({"past_shows_count": len(past_shows), "upcoming_shows_count": len(upcoming_shows),})
  #End todo
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
  error = False

  try:
    data = Venue()
    #Get venue name from form
    data.name = request.form.get('name')
    #Get venue genres from form
    data.genres = ', '.join(request.form.getlist('genres'))
    #Get venue address from form
    data.address = request.form.get('address')
    #Get venue city from form
    data.city = request.form.get('city')
    #Get venue state from form
    data.state = request.form.get('state')
    #Get venue phone from form
    data.phone = request.form.get('phone')
    #Get venue facebook link from form
    data.facebook_link = request.form.get('facebook_link')
    #Get venue image link from form
    data.image_link = request.form.get('image_link')
    #Get venue website link from form
    data.website = request.form.get('website_link')
    #Get seeking talent from form
    data.seeking_talent = True if request.form.get('seeking_talent')!= None else False
    #Get venue description
    data.seeking_description = request.form.get('seeking_description')

    #Add to database
    db.session.add(data)
    db.session.commit()
    # flash success 
    flash('Awesome the venue : ' + request.form['name'] + ' is listed.')

  except:
    error = True
    db.session.rollback()
    flash('Sorry an error occurred. the venue ' + request.form['name'] + ' not found !')
    abort(500)
  finally:
    #Close the session
    db.session.close()  

  #End TODO
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    #delete venue
    Show.query.filter_by(venue_id=venue_id).delete()
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue ' + venue_name + ' was deleted')

  except:
    error=True
    db.session.rollback()
    flash('an error occured and Venue ' + venue_name + ' was not deleted')
  finally:
    #Close the session
    db.session.close()

  if not error:
    return render_template('pages/home.html'), 200
  else:
    abort(500)
  #End TODO


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  artists = db.session.query(Artist).order_by('id').all()
  for artist in artists:   
      data.append({
          "id":artist.id,
          "name":artist.name,
          })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band"
  #Get search term
  search_term = request.form.get('search_term')
  #Set search criteria
  search_criteria = "%{}%".format(search_term.lower())
  #Query the search result
  result = Artist.query.filter(or_(Artist.name.ilike(search_criteria), Artist.city.ilike(search_criteria ), Artist.state.ilike(search_criteria ))).all()
  #Built the response
  response = {'count':len(result),'data':result}
  #End TODO
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #Query Artist by ID
  artist = db.session.query(Artist).filter(Artist.id == artist_id).all()
  #Get the current time
  current_time = datetime.now(timezone.utc)

  data= dict()
  down_show = list()
  up_show = list()

  for col in artist:
        #Get upcomming shows
        upcoming_shows = col.shows.filter(Show.start_time > current_time).all()
        #Get pass swow
        past_shows = col.shows.filter(Show.start_time < current_time).all()
        #Update data
        data_artist = {
        "id": col.id,
        "name": col.name,
        "genres": col.genres.split(", "),
        "city": col.city,
        "state": col.state,
        "phone": col.phone,
        "website": col.website,
        "facebook_link": col.facebook_link,
        "seeking_venue": col.seeking_venue,
        "seeking_description": col.seeking_description,
        "image_link": col.image_link,
        }
        data.update(data_artist)

        for show in upcoming_shows:
            if len(upcoming_shows) == 0:
                  data.update({"upcoming_shows": [],})
            else:
                  venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id == show.venue_id).one()
                  venue_data = {
                  "venue_id": show.venue_id,
                  "venue_name": venue.name,
                  "venue_image_link": venue.image_link,
                  "start_time": show.start_time.strftime('%m/%d/%Y'),
                  }
                  up_show.append(venue_data)
        for show in past_shows:
            if len(past_shows) == 0:
                  data.update({"past_shows": [],})
            else:
                  venue = db.session.query(Venue.name, Venue.image_link).filter(Venue.id == show.venue_id).one()
                  venue_data = {
                  "venue_id": show.venue_id,
                  "venue_name": venue.name,
                  "venue_image_link": venue.image_link,
                  "start_time": show.start_time.strftime('%m/%d/%Y'),
                  }
                  down_show.append(venue_data)
        #Update Upcoming shows
        data.update({"upcoming_shows": up_show})
        #Update Past shows
        data.update({"past_shows": down_show})
        data.update({"past_shows_count": len(past_shows), "upcoming_shows_count": len(upcoming_shows),})
  #End TODO
  return render_template('pages/show_artist.html', artist=data)



@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  form = ArtistForm()
  #Query artist by ID
  data = Artist.query.get(artist_id)

  artist_data ={
    "id": data.id,
    "name": data.name,
    "genres": data.genres.split(", "),
    "city": data.city,
    "state": data.state,
    "phone": data.phone,
    "website_link": data.website,
    "facebook_link": data.facebook_link,
    "seeking_venue": data.seeking_venue,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link,
  }
  #End TODO
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    #Get artist by ID
    data = Artist.query.get(artist_id)

    # Get artist name from the form
    data.name = request.form.get('name')
    # Get artist genre from the form
    data.genres = ', '.join(request.form.getlist('genres'))
    # Get artist city from the form
    data.city = request.form.get('city')
    # Get artist state from the form
    data.state = request.form.get('state')
    # Get artist phone from the form
    data.phone = request.form.get('phone')
    # Get artist  facebook link from the form
    data.facebook_link = request.form.get('facebook_link')
    # Get artist image link from the form
    data.image_link = request.form.get('image_link')
    # Get artist website from the form
    data.website = request.form.get('website_link')
    # Get artist seeking venue from the form
    data.seeking_venue = True if request.form.get('seeking_venue')!=None else False
    # Get artist description from the form
    data.seeking_description = request.form.get('seeking_description')
    #Add data to database
    db.session.add(data)
    db.session.commit()
    flash('Awesome artist ' + request.form['name'] + ' is updated!')
  except:
    db.session.rollback()
    flash('Sorry, unsuccesfull update')
  finally:
    db.session.close()
  #End TODO
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
# TODO: populate form with values from venue with ID <venue_id>
def edit_venue(venue_id):
  form = VenueForm()
  #Select venue by ID
  data = Venue.query.get(venue_id)

  venue={
    "id": data.id,
    "name": data.name,
    "genres": data.genres.split(", "),
    "address": data.address,
    "city": data.city,
    "state": data.state,
    "phone": data.phone,
    "website": data.website,
    "facebook_link": data.facebook_link,
    "seeking_talent": data.seeking_talent,
    "seeking_description": data.seeking_description,
    "image_link": data.image_link,
  }

  # End TODO
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:

    #Select Venue by ID
    data = Venue.query.get(venue_id)
    #Get Name from form
    data.name = request.form.get('name')
    #Get genre from form
    data.genres = ', '.join(request.form.getlist('genres'))
    #Get address from form
    data.address = request.form.get('address')
    #Get city from form
    data.city = request.form.get('city')
    #Get state from form
    data.state = request.form.get('state')
    #Get phone from form
    data.phone = request.form.get('phone')
    #Get facebook link  from form
    data.facebook_link = request.form.get('facebook_link')
    #Get image link from form
    data.image_link = request.form.get('image_link')
    #Get Website from form
    data.website = request.form.get('website_link')
    #Get seeking talent from form
    data.seeking_talent = True if request.form.get('seeking_talent')!= None else False
    #Get description from form
    data.seeking_description = request.form.get('seeking_description')
    #Add data to data base
    db.session.add(data)
    db.session.commit()
    flash('Awesome the venue ' + data.name  + '  updated')
  except:
    db.session.rollback()
    flash('Sorry an error occur when trying to update venue')
  finally:
    db.session.close()
  #End TODO
  return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)



@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    artist = Artist()
    #Get Artist Name from form
    artist.name = request.form.get('name')
    #Get Artist Genre from form
    artist.genres = ', '.join(request.form.getlist('genres'))
    #Get Artist City from form
    artist.city = request.form.get('city')
    #Get Artist State from form
    artist.state = request.form.get('state')
    #Get Artist Phone from form
    artist.phone = request.form.get('phone')
    #Get Artist Facebook link from form
    artist.facebook_link = request.form.get('facebook_link')
    #Get Artist Image Link from form
    artist.image_link = request.form.get('image_link')
    #Get Artist Website from form
    artist.website = request.form.get('website_link')
    #Get Artist Seeking Venue from form
    artist.seeking_venue = True if request.form.get('seeking_venue')!= None else False
    #Get Artist Get description from form
    artist.seeking_description = request.form.get('seeking_description')
    #Add to Dtabase
    db.session.add(artist)
    db.session.commit()
    flash('Awesome artist ' + request.form.get('name')  + ' is updated!')
  except:
    error = True
    db.session.rollback()
    flash('Sorry, unsuccesfull update')
  finally:
    db.session.close()

  #End Todo
  return render_template('pages/home.html')

@app.route('/artists/<artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a artist_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    #Query show by artist ID and delete
    Show.query.filter_by(artist_id=artist_id).delete()
    #Query artist info by ID and delete
    Artist.query.filter_by(id=artist_id).delete()
    #Commit to database
    db.session.commit()
    flash('Wel done,  Artist succesfully delete')
  except:
    error=True
    flash('Error,  Unable to delete artist from database')
    db.session.rollback()

  finally:
    db.session.close()

  if not error:
    #End TODO
    return render_template('pages/home.html'), 200
  else:
    abort(500)



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

        artist_data = {
          "venue_id": show.venue_id,
          "venue_name": venue.name,
          "artist_id": show.artist_id,
          "artist_name":artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.start_time.strftime('%m/%d/%Y')
        }

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
