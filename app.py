#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for

from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# Imports models
#----------------------------------------------------------------------------#

from models import Artist, Show, Venue, db

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)

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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  get_distinct_state = Venue.query.distinct(Venue.city, Venue.state).all()
  data = [venue.get_filter_by_state for venue in get_distinct_state]
  print(data)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
  number_venues = len(venues)
  response = {
      "count": number_venues,
      "data": [artist.venues_props for artist in venues]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  
  data = venue.venues_props
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
  
  request_form = VenueForm(request.form)
  try: 
    venue = Venue(
      name=request_form.name.data,
      genres=','.join(request_form.genres.data),
      address=request_form.address.data,
      city=request_form.city.data,
      state=request_form.state.data,
      phone=request_form.phone.data,
      website=request_form.website_link.data,
      facebook_link=request_form.facebook_link.data,
      image_link=request_form.image_link.data,
      seeking_talent=request_form.seeking_talent.data,
      seeking_description=request_form.seeking_description.data)
    
    db.session.add(venue)
    db.session.commit()
      
    # on successful db insert, flash success
    flash('Venue ' + request_form.name.data + ' was successfully listed!')
  except Exception as ex:
    db.session.rollback()
    flash('An error occurred. Venue ' + request_form.name.data + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['GET', 'DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    
    flash('Venue was successfully delected!')
  except:
    db.session.rollback()
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data = [artist.artists_props for artist in artists]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
  number_artists = len(artists)
  response = {
      "count": number_artists,
      "data": [artist.artists_props for artist in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artists = Artist.query.get(artist_id)
  data = artists.artists_props
  
  print(data)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  filter_artist = Artist.query.get(artist_id)
  artist =filter_artist.artists_props
  form = ArtistForm(data=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  request_form = ArtistForm(request.form)
  try:
    artist = Artist.query.filter(Artist.id==artist_id).one()
    artist.name=request_form.name.data
    artist.genres=','.join(request_form.genres.data)
    artist.city=request_form.city.data
    artist.state=request_form.state.data
    artist.phone=request_form.phone.data
    artist.website = request_form.website_link.data
    artist.facebook_link=request_form.facebook_link.data
    artist.image_link=request_form.image_link.data
    artist.seeking_venue=request_form.seeking_venue.data
    artist.seeking_description=request_form.seeking_description.data

    
    db.session.commit()
    
    # on successful db update, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request_form.name.data + ' could not be updateed.')
    print(sys.exc_info())
  finally:
    db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  filter_venue = Venue.query.get(venue_id)
  print(filter_venue)
  venue =filter_venue.venues_props
  form = VenueForm(data=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  request_form = VenueForm(request.form)
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request_form.name.data
    venue.address = request_form.address.data
    venue.genres = '.'.join(request_form.genres.data)
    venue.city = request_form.city.data
    venue.state = request_form.state.data
    venue.phone = request_form.phone.data
    venue.website = request_form.website_link.data
    venue.facebook_link = request_form.facebook_link.data
    venue.image_link = request_form.image_link.data
    venue.seeking_talent=request_form.seeking_talent.data
    venue.seeking_description=request_form.seeking_description.data

    db.session.commit()
    
    # on successful db update, flash success
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request_form.name.data + ' could not be updateed.')
    print(sys.exc_info())
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
  
  request_form = ArtistForm(request.form)
  try:
    artist = Artist(
      name=request_form.name.data,
      genres=','.join(request_form.genres.data),
      city=request_form.city.data,
      state=request_form.state.data,
      phone=request_form.phone.data,
      website=request_form.website_link.data,
      facebook_link=request_form.facebook_link.data,
      image_link=request_form.image_link.data,
      seeking_venue=request_form.seeking_venue.data,
      seeking_description=request_form.seeking_description.data)

    
    db.session.add(artist)
    db.session.commit()
    
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request_form.name.data + ' could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  data = [show.shows_props_total for show in shows]
  print(data)
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

  try:
    show = Show(venue_id=request.form['venue_id'], artist_id=request.form['artist_id'], start_time=request.form['start_time'])
    print(show)
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
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
