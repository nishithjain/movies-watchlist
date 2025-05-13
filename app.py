import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import requests
from models import User, Movie, Review, db, init_db

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Welcome%40123@localhost/movie_watchlist'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)
with app.app_context():
    init_db()

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# OMDb API configuration
OMDB_API_KEY = os.environ.get('OMDB_API_KEY', '')
OMDB_BASE_URL = "http://www.omdbapi.com/"
OMDB_POSTER_URL = "http://img.omdbapi.com/"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email already exists. Please log in.', 'danger')
            return redirect(url_for('login'))

        new_user = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('login'))

        login_user(user, remember=remember)
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    watchlist = Movie.query.filter_by(user_id=current_user.id, watched=False).all()
    watched = Movie.query.filter_by(user_id=current_user.id, watched=True).all()
    for movie in watchlist:
        print(movie.title, movie.poster_url)
    return render_template('dashboard.html', watchlist=watchlist, watched=watched)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            # Fetch data from OMDb API
            url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={query}"
            response = requests.get(url)
            data = response.json()

            # Ensure the 'Search' key exists and is passed to the template
            if 'Search' in data:
                movies = data['Search']
            else:
                movies = []

            return render_template('search_results.html', movies=movies)
    
    # For GET request, show the search form page
    return render_template('search.html')

@app.route('/movie/<imdb_id>')
@login_required
def movie_details(imdb_id):
    response = requests.get(
        OMDB_BASE_URL,
        params={
            "apikey": OMDB_API_KEY,
            "i": imdb_id,
            "plot": "full"
        }
    )

    if response.status_code != 200:
        flash('Failed to fetch movie details. Please try again later.', 'danger')
        return redirect(url_for('watchlist'))

    if response.status_code == 200:
        movie = response.json()
        if movie.get("Response") == "True":
            poster_path = movie.get('Poster', 'default_poster.jpg')
            title = movie.get('Title', 'Unknown Title')
            year = movie.get('Year', 'Unknown Year')
            runtime = movie.get('Runtime', 'Unknown Runtime')
            rating = movie.get('imdbRating', 'N/A')
            genres = movie.get('Genre', 'Unknown Genre')
            overview = movie.get('Plot', 'No plot available')

            return render_template(
                'movie_details.html',
                movie=movie,
                poster_path=poster_path,
                title=title,
                year=year,
                runtime=runtime,
                rating=rating,
                genres=genres,
                overview=overview
            )
        else:
            flash('Movie not found.', 'warning')
            return redirect(url_for('search'))
    else:
        flash('Failed to fetch movie details. Please try again.', 'danger')
        return redirect(url_for('search'))




@app.route('/add_to_watchlist/<imdb_id>', methods=['POST'])
@login_required
def add_to_watchlist(imdb_id):
    # Get user_id
    user_id = current_user.id  # Get the current logged-in user's ID
    
    # Fetch movie info from OMDb
    response = requests.get(
        OMDB_BASE_URL,
        params={
            "apikey": OMDB_API_KEY,
            "i": imdb_id
        }
    )
    
    if response.status_code != 200:
        flash('Failed to fetch movie details. Please try again later.', 'danger')
        return redirect(url_for('watchlist'))
    
    if response.status_code == 200:
        movie = response.json()
        
        if movie.get("Response") == "True":
            user = User.query.get(user_id)  # Use user_id to fetch the user
            
            # Check if movie already in watchlist
            if any(w.imdb_id == imdb_id for w in user.watchlist):
                flash('Movie already in your watchlist.', 'info')
            else:
                # Create the new movie and associate it with the user
                new_movie = Movie(
                    user_id=user_id,  # Set user_id explicitly
                    imdb_id=imdb_id,
                    title=movie['Title'],
                    poster_url=movie['Poster']
                )
                user.watchlist.append(new_movie)
                db.session.commit()
                flash(f"{movie['Title']} added to your watchlist!", 'success')
        else:
            flash('Movie not found.', 'warning')
    else:
        flash('Failed to fetch movie details.', 'danger')

    flash(f'Movie with IMDb ID {imdb_id} added to watchlist!', 'success')
    return redirect(url_for('watchlist'))



@app.route('/watchlist')
@login_required
def watchlist():
    print("Hello from watchlist")
    user = User.query.get(current_user.id)
    return render_template('dashboard.html', watchlist=user.watchlist)

@app.route('/toggle_watched/<int:movie_id>', methods=['POST'])
@login_required
def toggle_watched(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if movie.user_id != current_user.id:
        flash('Not authorized.', 'danger')
        return redirect(url_for('dashboard'))

    movie.watched = not movie.watched
    db.session.commit()
    flash(f'Movie marked as {"watched" if movie.watched else "unwatched"}.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/remove_movie/<int:movie_id>', methods=['POST'])
@login_required
def remove_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if movie.user_id != current_user.id:
        flash('Not authorized.', 'danger')
        return redirect(url_for('dashboard'))

    reviews = Review.query.filter_by(user_id=current_user.id, imdb_id=movie.imdb_id).all()
    for review in reviews:
        db.session.delete(review)

    db.session.delete(movie)
    db.session.commit()
    flash('Movie removed from your list.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/add_review/<string:imdb_id>', methods=['POST'])
@login_required
def add_review(imdb_id):
    rating = int(request.form.get('rating', 0))
    review_text = request.form.get('review_text', '')

    if rating < 1 or rating > 10:
        flash('Rating must be between 1 and 10.', 'danger')
        return redirect(url_for('movie_details', imdb_id=imdb_id))

    existing_review = Review.query.filter_by(user_id=current_user.id, imdb_id=imdb_id).first()
    if existing_review:
        existing_review.rating = rating
        existing_review.review_text = review_text
        flash('Review updated successfully!', 'success')
    else:
        new_review = Review(user_id=current_user.id, imdb_id=imdb_id, rating=rating, review_text=review_text)
        db.session.add(new_review)
        flash('Review added successfully!', 'success')

    db.session.commit()
    return redirect(url_for('movie_details', imdb_id=imdb_id))

@app.route('/profile')
@login_required
def profile():
    total_movies = Movie.query.filter_by(user_id=current_user.id).count()
    watched_movies = Movie.query.filter_by(user_id=current_user.id, watched=True).count()
    total_reviews = Review.query.filter_by(user_id=current_user.id).count()

    return render_template('profile.html',
                           total_movies=total_movies,
                           watched_movies=watched_movies,
                           total_reviews=total_reviews)

if __name__ == '__main__':
    app.run(debug=True)
