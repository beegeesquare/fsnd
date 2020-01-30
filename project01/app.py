# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
# Import migrate class
from flask_migrate import Migrate
import datetime as dt
import sys

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
# Add the migrate object to the app
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String(50)))
    website = db.Column(db.String(50))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(150))

    # Adding relationship to the show table
    show_id = db.relationship('Show', backref='venues', lazy=True)
    '''
    def __dict__(self):
        return {"id": self.id, "name": self.name, "city": self.city, "state": self.state, "address": self.address,
              "phone": self.phone, "image_link": self.image_link, "facebook_link": self.facebook_link,
              "genres": self.genres, "website": self.website, "seeking_talent": self.seeking_talent,
              "seeking_description": self.seeking_description
              }
    '''


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    # Here geners is defined as the string
    # However we will be do a migration to Array
    # To do that we need to drop the string column --> migrate
    # Then add the ARRAY column back
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # Adding genres
    genres = db.Column(db.ARRAY(db.String(50)))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(50))
    # Change the name of the column to seeking_venues.
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(150))

    # Adding the relationship
    show_id = db.relationship('Show', backref='artists', lazy=True)


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# Adding the show table to the database
class Show(db.Model):
    __tablename__ = 'Show'

    show_id = db.Column(db.Integer, primary_key=True)  # This make nullable False
    artist_image_link = db.Column(db.String(150))
    start_time = db.Column(db.String(100))

    # Now add the Foreign keys for the Venue and Artist
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
def get_upcoming_shows(venue):
    shows_ = venue.show_id
    upcoming_shows = []
    # upcoming_shows = 0
    for s in shows_:
        if dt.datetime.strptime(s.start_time, '%Y-%m-%dT%H:%M:%S.%fZ') > dt.datetime.now():
            upcoming_shows.append({'artist_id': s.artist_id, 'artist_name': Artist.query.get(s.artist_id).name,
                                   'artist_image_link': Artist.query.get(s.artist_id).image_link,
                                   'start_time': s.start_time
                                   },
                                  )
            # upcoming_shows +=1

    return upcoming_shows


def get_past_shows(venue):
    shows_ = venue.show_id
    past_shows = []
    for s in shows_:
        if dt.datetime.strptime(s.start_time, '%Y-%m-%dT%H:%M:%S.%fZ') <= dt.datetime.now():
            past_shows.append({'artist_id': s.artist_id, 'artist_name': Artist.query.get(s.artist_id).name,
                               'artist_image_link': Artist.query.get(s.artist_id).image_link,
                               'start_time': s.start_time
                               })
    return past_shows


def get_upcoming_shows_art(artist):
    shows_ = artist.show_id
    upcoming_shows = []
    # upcoming_shows = 0
    for s in shows_:
        if dt.datetime.strptime(s.start_time, '%Y-%m-%dT%H:%M:%S.%fZ') > dt.datetime.now():
            upcoming_shows.append({'venue_id': s.venue_id, 'venue_name': Venue.query.get(s.venue_id).name,
                                   'venue_image_link': Venue.query.get(s.venue_id).image_link,
                                   'start_time': s.start_time
                                   },
                                  )

    return upcoming_shows


def get_past_shows_art(artist):
    shows_ = artist.show_id
    past_shows = []
    for s in shows_:
        if dt.datetime.strptime(s.start_time, '%Y-%m-%dT%H:%M:%S.%fZ') <= dt.datetime.now():
            past_shows.append({'venue_id': s.venue_id, 'venue_name': Venue.query.get(s.venue_id).name,
                                   'venue_image_link': Venue.query.get(s.venue_id).image_link,
                                   'start_time': s.start_time
                                   },
                                  )
    return past_shows


@app.route('/venues')
def venues():
    # Here we need to get the unique cites from the venue table, combination of city and state
    # This gives the list of unique (city, state) pairs from the data
    data = []
    city_state = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
    for cs in city_state:
        data.append({'city': cs[0], 'state': cs[1]})
        get_vens_ = Venue.query.filter_by(city=cs[0], state=cs[1]).all()
        # Take the latest element in the list that just got appended
        data[-1]['venues'] = []
        for v in get_vens_:
            venue_details = {'id': v.id, 'name': v.name, 'num_upcoming_shows': len(get_upcoming_shows(v))}
            # Get the shows for this venue
            data[-1]['venues'].append(venue_details)

    return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    ven_query = Venue.query.filter(Venue.name.ilike(r"%{0}%".format(request.form.get('search_term', ''))))
    # print(ven_query)
    data = []
    for v in ven_query:
        data.append({"id": v.id, "name": v.name, "num_upcoming_shows": len(get_upcoming_shows(v))})
    response = {"count": ven_query.count(), "data": data}

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # replace with real venue data from the venues table, using venue_id
    data = {} # Initialize, so that there wouldn't be any error is the venue_id is not found in the db
    ven_data = Venue.query.get(venue_id)

    if ven_data is not None:
        data = ven_data.__dict__  # Converts the Venue object to a dict defined in dunder wrapper method
        # Add the other details to this dict
        # print(data)
        data["upcoming_shows_count"] = len(get_upcoming_shows(ven_data))
        data["past_shows_count"] = len(get_past_shows(ven_data))
        data["past_shows"] = get_past_shows(ven_data)
        data["upcoming_shows"] = get_upcoming_shows(ven_data)


    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # insert form data as a new Venue record in the db, instead
    # modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    data = request.form

    try:
        # Convert the seeking_talent to boolean
        seeking_talent = False
        if data.get('seeking_talent') == 'y':
            seeking_talent = True

        venue = Venue(name=data.get('name'), city=data.get('city'), state=data.get('state'),
                      address=data.get('address'), phone=data.get('phone'), genres=data.getlist('genres'),
                      facebook_link=data.get('facebook_link'), website=data.get('website'),
                      seeking_talent=seeking_talent,
                      seeking_description=data.get('seeking_description')
                      )
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        # on unsuccessful db insert, flash an error instead.
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        db.session.rollback()
        flash('Venue ' + request.form['name'] + ' post has been unsuccessful; Try again')
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue_d = Venue.query.get(venue_id)
        db.session.delete(venue_d)
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    all_artists = Artist.query.all()
    data = [{"id": art.id, "name": art.name} for art in all_artists]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    art_search = Artist.query.filter(Artist.name.ilike(r"%{0}%".format(request.form.get('search_term')))).all()
    response = {"count": len(art_search), "data": [{"id": art.id, "name": art.name,
                                                    "num_upcoming_shows": len(get_upcoming_shows_art(art))}
                                                   for art in art_search]}

    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # replace with real artist data from the artist table, using artist_id
    # First get the data for the given artist id from the table
    data = {} # Initialize to avoid any exceptions if the data for given artist id is not found in db
    artist = Artist.query.get(artist_id)
    if artist is not None:
        data = artist.__dict__
        # Now add other attributes to the data dict
        past_shows = get_past_shows_art(artist)
        data["past_shows"] = past_shows
        data["past_shows_count"] = len(past_shows)
        upcoming_shows = get_upcoming_shows_art(artist)
        data["upcoming_shows"] = upcoming_shows
        data["upcoming_shows_count"] = len(upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get(artist_id)
    if artist: # Basically if the artist id exists in the data base
        form.name.data = artist.name
        form.city.data = artist.city
        form.facebook_link.data = artist.facebook_link
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.website.data = artist.website
        form.image_link.data = artist.image_link
        if artist.seeking_venue:
            form.seeking_venue.data = artist.seeking_venue
            form.seeking_description.data = artist.seeking_description
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    else:
        flash('Artist ' + str(artist_id) + ' not found in the database')
        return render_template('pages/home.html')


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    data = request.form
    # print(artist)
    if artist:  # Means that it's not none type, that means there is
        try:
            # Convert the seeking_talent to boolean
            seeking_venue = False
            if data.get('seeking_venue') == 'y':
                seeking_venue = True
            artist.name = data.get('name')
            artist.city = data.get('city')
            artist.state = data.get('state')
            artist.address = data.get('address')
            artist.phone = data.get('phone')
            artist.genres = data.getlist('genres')
            artist.facebook_link = data.get('facebook_link')
            artist.website = data.get('website')
            artist.seeking_venue = seeking_venue
            artist.seeking_description = data.get('seeking_description')
            artist.image_link = data.get('image_link')

            db.session.commit()
            flash('Artist ' + request.form['name'] + ' was successfully edited!')

        except:
            db.session.rollback()
            print(sys.exc_info())
            flash('Artist ' + request.form['name'] + ' edit was unsuccessful!')
        finally:
            db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        return render_template('error/404.html'), 404


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # populate form with values from venue with ID <venue_id>
    venue = Venue.query.get(venue_id)
    if venue:  # Means the venue id exists in the database
        form.name.data = venue.name
        form.city.data = venue.city
        form.facebook_link.data = venue.facebook_link
        form.state.data = venue.state
        form.phone.data = venue.phone
        form.website.data = venue.website
        form.image_link.data = venue.image_link
        if venue.seeking_talent:
            form.seeking_talent.data = venue.seeking_talent
            form.seeking_description.data = venue.seeking_description
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    else:
        flash('Venue ' + str(venue_id) + ' not found in the database')
        return render_template('pages/home.html')



@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue = Venue.query.get(venue_id)
    data = request.form
    if venue:  # Means that it's not none type, that means there is
        try:
            # Convert the seeking_talent to boolean
            seeking_talent = False
            if data.get('seeking_talent') == 'y':
                seeking_talent = True
            venue.name = data.get('name')
            venue.city = data.get('city')
            venue.state = data.get('state')
            venue.address = data.get('address')
            venue.phone = data.get('phone')
            venue.genres = data.getlist('genres')
            venue.facebook_link = data.get('facebook_link')
            venue.website = data.get('website')
            venue.seeking_talent = seeking_talent
            venue.seeking_description = data.get('seeking_description')
            venue.image_link = data.get('image_link')

            db.session.commit()
            flash('Venue ' + request.form['name'] + ' was successfully edited!')

        except:
            db.session.rollback()
            print(sys.exc_info())
            flash('Venue ' + request.form['name'] + ' edit was unsuccessful!')
        finally:
            db.session.close()
        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        return render_template('error/404.html'), 404

    # return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # insert form data as a new Venue record in the db, instead
    new_artist = Artist()
    # modify data to be the data object returned from db insertion
    data = request.form
    try:
        new_artist.name = data.get('name')
        new_artist.city = data.get('city')
        new_artist.state = data.get('state')
        new_artist.phone = data.get('phone')
        new_artist.genres = data.getlist('genres')
        new_artist.facebook_link = data.get('facebook_link')
        new_artist.website = data.get('website')
        new_artist.image_link = data.get('image_link')
        new_artist.seeking_venue = False
        if data.get('seeking_venue') == 'y':
            new_artist.seeking_venue = True
            new_artist.seeking_description = data.get('seeking_description')

        db.session.add(new_artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully edited !')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('Artist ' + request.form['name'] + ' was unsuccessful!')
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    
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

    # on successful db insert, flash success
    flash('Show was successfully listed!')
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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
