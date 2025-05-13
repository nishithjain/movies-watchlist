from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship for Movies owned by the user (one-to-many)
    movies = db.relationship('Movie', back_populates='owner', lazy=True)
    
    # Relationship for Reviews written by the user (one-to-many)
    reviews = db.relationship('Review', back_populates='user', lazy=True)
    
    # Watchlist relationship for many-to-many (users and movies)
    watchlist = db.relationship('Movie', secondary='watchlist', backref=db.backref('watchlisted_by', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    imdb_id = db.Column(db.String(20))  # ✅ Add this line
    title = db.Column(db.String(200), nullable=False)
    poster_url = db.Column(db.String(200))
    release_date = db.Column(db.String(20))
    watched = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to the User who owns the movie (many-to-one)
    owner = db.relationship('User', back_populates='movies')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return f'<Movie {self.title}>'


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    imdb_id  = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # Rating out of 10
    review_text = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to the user who wrote the review
    user = db.relationship('User', back_populates='reviews')
    
    def __repr__(self):
        return f'<Review {self.id} for Movie {self.imdb_id}>'


# Watchlist Association Table (many-to-many relationship)
watchlist = db.Table('watchlist',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True)
)

def init_db():
    db.create_all()
