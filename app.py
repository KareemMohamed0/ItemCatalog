#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, redirect
from flask import request, flash, url_for, session, jsonify
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from flask_oauth import OAuth
import json

from database_setup import *
import datetime

app = Flask(__name__)

GOOGLE_CLIENT_ID = 'add_your_id_here'
GOOGLE_CLIENT_SECRET = 'add_your_seceret_here'
REDIRECT_URI = '/oauth2callback'

engine = create_engine('sqlite:///moviesCatalog.db', echo=True)
Base.metadata.bind = engine
dbSession = scoped_session(sessionmaker(bind=engine))

oauth = OAuth()

# Google Config

google = oauth.remote_app(
    'google',
    base_url='https://www.google.com/accounts/',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    request_token_url=None,
    request_token_params={
                    'scope':
                    'https://www.googleapis.com/auth/userinfo.email',
                    'response_type': 'code'
                    },
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_method='POST',
    access_token_params={'grant_type': 'authorization_code'},
    consumer_key=GOOGLE_CLIENT_ID,
    consumer_secret=GOOGLE_CLIENT_SECRET,
    )

# register if first time login by google


def addUserIfNotExist(user):

    try:

        dbSession.query(User).filter(User.email == user.get('email')).one()
    except:
        dbSession.add(User(id=str(user.get('id')),
                      email=str(user.get('email'))))
        dbSession.commit()


# google logout

@app.route('/googledisconnect')
def logout():
    del session['email']
    del session['access_token']
    del session['id']
    return redirect(url_for('home'))


# google Login

@app.route('/googleconnect')
def index():

    if 'email' in session:
        flash('you already authenticated')
        return redirect('/')

    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))

    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError

    headers = {'Authorization': 'OAuth ' + access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:

            # Unauthorized - bad token

            session.pop('access_token', None)
            return redirect(url_for('login'))
        return res.read()
    user = json.loads(res.read())
    addUserIfNotExist(user)
    session['email'] = user.get('email')

    session['id'] = user.get('id')
    return redirect(url_for('home'))


@app.route('/login')
def login():
    callback = url_for('authorized', _external=True)
    return google.authorize(callback=callback)


@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = (access_token, '')
    return redirect(url_for('index'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')


# Home page

@app.route('/')
def home():
    allCategory = dbSession.query(Category).all()
    dbSession.close()
    LatestMovies = \
        dbSession.query(Movie).order_by(desc(Movie.createdAt)).limit(8)
    dbSession.close()
    return render_template('home.html', allCategory=allCategory,
                           LatestMovies=LatestMovies)


# Add Category

@app.route('/category/add', methods=['GET', 'POST'])
def addCategory():
    if request.form:
        req = request.form
        if not req.get('title'):
            flash('Movie title is required')
            return redirect(url_for('addCategory'))
        dbSession.add(Category(title=req.get('title')))
        dbSession.commit()

        flash('Category added successfuly')
        return redirect(url_for('home'))
    return render_template('addCategory.html')


# Delete Movie

@app.route('/movies/<string:movie>/delete', methods=['GET', 'POST'])
def deleteMovie(movie):

    if 'email' not in session:
        flash('authentication required')
        return redirect('/')

    deletedMovie = dbSession.query(Movie).filter(Movie.title == movie).one()

    if session['id'] != deletedMovie.user_id:
        flash('You hav not permission to delete this item')
        return redirect('/')

    if request.method == 'POST':
        dbSession.query(Movie).filter(Movie.title == movie).delete()
        dbSession.commit()

        flash('Movie deleted successfuly')
        return redirect(url_for('home'))
    return render_template('deleteMovie.html', movie=movie)


# Update  Movie

@app.route('/movies/<string:movie>/edit', methods=['GET', 'POST'])
def updateMovie(movie):

    if 'email' not in session:
        flash('authentication required')
        return redirect('/')

    editedMovie = dbSession.query(Movie).filter(Movie.title == movie).one()
    if session['id'] != editedMovie.user_id:
        flash('You hav not permission to update this item')
        return redirect('/')

    if request.form:
        req = request.form
        if not req.get('title'):
            flash('Movie title is required')
            return redirect(url_for('addMovie'))
        if not req.get('image'):
            flash('Movie image url is required')
            return redirect(url_for('addMovie'))
        if not req.get('description'):
            flash('Movie description is required')
            return redirect(url_for('addMovie'))
        if not req.get('category_id'):
            flash('Movie category is required')
            return redirect(url_for('addCategory'))

        editedMovie.title = req.get('title')
        editedMovie.category_id = req.get('category_id')
        editedMovie.description = req.get('description')
        editedMovie.image = req.get('image')
        dbSession.add(editedMovie)
        dbSession.commit()
        flash('Movie updated successfuly')
        return redirect(url_for('home'))
    selectedMovie = dbSession.query(Movie).filter(Movie.title == movie).one()
    allCategory = dbSession.query(Category).all()
    return render_template('updateMovie.html', movie=selectedMovie,
                           allCategory=allCategory)


# Filter movies by categories

@app.route('/movies/<string:category>/items')
def getCategoryItems(category):
    allCategory = dbSession.query(Category).all()
    selectedCategory = dbSession.query(Category).filter(
        Category.title == category
        ).one()
    movies = dbSession.query(Movie).filter(
        Movie.category_id == selectedCategory.id
        ).all()
    movieCount = len(movies)
    return render_template('categoryItems.html',
                           allCategory=allCategory, title=category,
                           movies=movies, movieCount=movieCount)


@app.route('/movies/<string:movie>')
def getMovieDetails(movie):
    selectedMovie = dbSession.query(Movie).filter(Movie.title == movie).one()
    return render_template('movieDetails.html', movie=selectedMovie)


# Add movie

@app.route('/movies/add', methods=['GET', 'POST'])
def addMovie():

    if 'email' not in session:
        flash('authentication required')
        return redirect('/')

    if request.form:
        req = request.form
        if not req.get('title'):
            flash('Movie title is required')
            return redirect(url_for('addMovie'))
        if not req.get('image'):
            flash('Movie image url is required')
            return redirect(url_for('addMovie'))
        if not req.get('description'):
            flash('Movie description is required')
            return redirect(url_for('addMovie'))
        if not req.get('category_id'):
            flash('Movie category is required')
            return redirect(url_for('addCategory'))

        now = datetime.datetime.now()
        movie = Movie(
            title=req.get('title'),
            category_id=req.get('category_id'),
            user_id=session['id'],
            description=req.get('description'),
            image=req.get('image'),
            createdAt=now,
            )
        dbSession.add(movie)
        dbSession.commit()
        flash('Movie added successfuly')
        return redirect(url_for('home'))
    allCategory = dbSession.query(Category).all()
    return render_template('addMovie.html', allCategory=allCategory)


# End Point api

@app.route('/categories/JSON')
def showCategoriesJSON():
    categories = dbSession.query(Category).all()
    return jsonify(categories=[category.serialize for category in
                   categories])


@app.route('/movies/JSON')
def showMoviesJSON():
    movies = dbSession.query(Movie).all()
    return jsonify(movies=[movie.serialize for movie in movies])


@app.route('/movies/<int:id>/JSON')
def showMovieJSON(id):
    movie = dbSession.query(Movie).filter(Movie.id == id).one()
    return jsonify(movie=movie.serialize)

if __name__ == '__main__':
    app.secret_key = 'Item55626Catalog'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
