import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    genres = db.Column(db.String())
    
    def __repr__(self):
        return f'<Venue id: {self.id}, name: {self.name}>'
    
    @property
    def venues_props(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres.split(','),
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'address': self.address,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'website': self.website,
            'upcoming_shows': [show.shows_props_total for show in Show.query.filter(Show.start_time > datetime.datetime.now(), Show.venue_id == self.id).all()],
            'past_shows': [show.shows_props_total for show in Show.query.filter(Show.start_time < datetime.datetime.now(), Show.venue_id == self.id).all()],
            'upcoming_shows_count': len(Show.query.filter(Show.start_time > datetime.datetime.now(),Show.venue_id == self.id).all()),
            'past_shows_count': len(Show.query.filter(Show.start_time < datetime.datetime.now(),Show.venue_id == self.id).all())
            }

    @property
    def get_venue_name(self):
        return self.name
    
    @property
    def get_venue_image_link(self):
        return self.image_link
    
    @property
    def get_filter_by_state(self):
        return {
            'city': self.city,
            'state': self.state,
            'venues': [venue.venues_props for venue in Venue.query.filter(Venue.city == self.city, Venue.state == self.state).all()]
            }
        

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    genres = db.Column(db.String())
    
    def __repr__(self):
        return f'<Venue id: {self.id}, name: {self.name}>'
    
    @property
    def artists_props(self):
        return {'id': self.id,
                'name': self.name,
                'city': self.city,
                'genres': self.genres.split(','),
                'state': self.state,
                'phone': self.phone,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'seeking_venue': self.seeking_venue,
                'seeking_description': self.seeking_description,
                'website': self.website,
                'upcoming_shows': [show.shows_props_total for show in Show.query.filter(Show.start_time > datetime.datetime.now(), Show.artist_id == self.id).all()],
                'past_shows': [show.shows_props_total for show in Show.query.filter(Show.start_time < datetime.datetime.now(), Show.artist_id == self.id).all()],
                'upcoming_shows_count': len(Show.query.filter(Show.start_time > datetime.datetime.now(), Show.artist_id == self.id).all()),
                'past_shows_count': len(Show.query.filter(Show.start_time < datetime.datetime.now(), Show.artist_id == self.id).all())
                }
        
    @property
    def get_artist_name(self):
        return self.name
    
    @property
    def get_artist_image_link(self):
        return self.image_link
            
    

class Show(db.Model):
    __tablename__ = 'shows'
    
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    venue = db.relationship('Venue', backref=db.backref('shows', cascade='all'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    artist = db.relationship('Artist', backref=db.backref('shows', cascade='all'))
    start_time = db.Column(db.DateTime())
    
    def __repr__(self):
        return f'<Venue id: {self.id}, start_time: {self.start_time}>'
    
        
    @property
    def shows_props_total(self):
        return {'id': self.id,
                'venue_id': self.venue_id,
                'artist_id': self.artist_id,
                'start_time': self.start_time.strftime("%m/%d/%Y, %H:%M:%S"),
                'venue_name': [venue.get_venue_name for venue in Venue.query.filter(Venue.id == self.venue_id).all()][0],
                'artist_name': [artist.get_artist_name for artist in Artist.query.filter(Artist.id == self.artist_id).all()][0],
                'artist_image_link': [artist.get_artist_image_link for artist in Artist.query.filter(Artist.id == self.artist_id).all()][0],
                'venue_image_link': [venue.get_venue_image_link for venue in Venue.query.filter(Venue.id == self.venue_id).all()][0]
                }
