# 🎬 Movie Watchlist App

A simple web application built with Flask that allows users to register, log in, and manage their personal movie watchlists. Users can search for movies, view details, and track their favorite films.

## 📁 Project Structure
```bash
movie-watchlist/
│       app.py # Main Flask application
│       models.py # SQLAlchemy models
│
├───.vscode/
│       launch.json # VSCode launch config
│
├───instance/
│       watchlist.db # SQLite database file
│
├───static/
│       requirements.txt # List of dependencies
│       script.js # JavaScript for frontend behavior
│       style.css # Styling for the app
│
└───templates/
        dashboard.html
        index.html
        login.html
        movie_details.html
        navbar.html
        profile.html
        register.html
        search.html
        search_results.html
```

---

## 🚀 Getting Started

```bash
git clone https://github.com/nishithjain/movies-watchlist.git
cd movie-watchlist
pip install -r static/requirements.txt
python app.py
Visit http://127.0.0.1:5000/ in your browser.
