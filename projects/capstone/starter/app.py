import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import setup_db, Movie, Actor, db
from flask_migrate import Migrate
from auth import AuthError, requires_auth
import json
from sqlalchemy.sql.expression import func

def create_app(test_config=None):
   # Set up flask app
  app = Flask(__name__)
  setup_db(app)
  migrate = Migrate(app,db)
  cors=CORS(app,resources={r"*":{"origins":"*"}})

# app = create_app()


  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE,PATCH')
    return response


  @app.route('/movies',methods=['GET'])
  @requires_auth('get:movies')
  def get_movies(jwt_token_payload):
    try:
      movies = Movie.query.order_by(Movie.title).all()
      movies_formatted = []

      if len(movies)==0:
        abort(404)

      for movie in movies:
        movies_formatted.append(movie.format())

      return jsonify({
        'success':True,
        'movies':movies_formatted
      })
    except Exception:
      abort(422)


  @app.route('/',methods=['GET'])
  def index(): 
    return('Welcome to the casting agency app!')


  @app.route('/actors',methods=['GET'])
  @requires_auth('get:actors')
  def get_actors(jwt_token_payload):
    try:
      actors = Actor.query.order_by(Actor.name).all()
      actors_formatted = []

      if len(actors)==0:
        abort(404)

      for actor in actors:
        actors_formatted.append(actor.format())

      return jsonify({
        'success':True,
        'actors':actors_formatted
      })
    except Exception:
      abort(422)


  @app.route('/movies/<int:movie_id>',methods=['DELETE'])
  @requires_auth('delete:movies')
  def delete_movie(jwt_token_payload,movie_id):
    try:
      movie = Movie.query.filter(Movie.id==movie_id).one_or_none()
      
      if movie is None:
        abort(404)
      movie.delete()

      return jsonify({
        'success':True,
        'deleted':movie.id
      })
    except Exception:
      abort(422)


  @app.route('/actors/<int:actor_id>',methods=['DELETE'])
  @requires_auth('delete:actors')
  def delete_actor(jwt_token_payload,actor_id):
    try:
      actor = Actor.query.filter(Actor.id==actor_id).one_or_none()
      if actor==None:
        abort(404)
    
      actor.delete()

      return jsonify({
        'success':True,
        'deleted':actor.id
      })
    except Exception:
      abort(422)


  @app.route('/movies',methods=['POST'])
  @requires_auth('post:movies')
  def post_movie(jwt_token_payload):

    try:
      data = request.get_json()
      title=data.get('title',None)
      release_date = data.get('release_date',None)

      if title==None or release_date==None:
        abort(422)

      movie = Movie(title=title,release_date=release_date)
      movie.insert()

      return jsonify({
        'success':True,
        'created':movie.id
      })
    except Exception:
      abort(422)


  @app.route('/actors',methods=['POST'])
  @requires_auth('post:actors')
  def post_actor(jwt_token_payload):
    try:
      data=request.get_json()
      name = data.get('name',None)
      birthdate = data.get('birthdate',None)
      gender = data.get('gender',None)

      if name==None or birthdate==None or gender==None:
        abort(422)

      actor = Actor(name=name,birthdate=birthdate,gender=gender)
      actor.insert()

      return jsonify({
        'success':True,
        'created':actor.id
      })
    except Exception:
      abort(422)


  @app.route('/movies/<int:movie_id>',methods=['PATCH'])
  @requires_auth('patch:movies')
  def patch_movie(jwt_token_payload,movie_id):
    try:
      data = request.get_json()
      if data is None:
        abort(404)

      title=data.get('title',None)
      release_date = data.get('release_date',None)

      movie = Movie.query.filter(Movie.id==movie_id).one_or_none()
      if not movie:
        abort(404)
      
      if title:
        movie.title=title

      if release_date:
        movie.release_date=release_date

      movie.update()

      return jsonify({
        'success':True,
        'movies':[movie.format()]
      })
    except Exception:
      abort(422)


  @app.route('/actors/<int:actor_id>',methods=['PATCH'])
  @requires_auth('patch:actors')
  def path_actor(jwt_token_payload,actor_id):

    try:
      data=request.get_json()
      if data==None:
        abort(404)
      name = data.get('name',None)
      birthdate = data.get('birthdate',None)
      gender = data.get('gender',None)

      actor = Actor.query.filter(Actor.id==actor_id).one_or_none()
      
      if not actor:
        abort(404)

      if name:
        actor.name=name

      if birthdate:
        actor.birthdate=birthdate

      if gender:
        actor.gender=gender

      actor.update()

      return jsonify({
        'success':True,
        'actors':[actor.format()]
      })
    except Exception:
      abort(422)


  # ERROR HANDLERS
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success':False,
      'error':400,
      'message':'Bad request'
    }),400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success':False,
      'error':404,
      'message':'Resource not found'
    }),404

  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
      'success':False,
      'error':405,
      'message':'Method not allowed'
    }),405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success':False,
      'error':422,
      'message':'Unprocessable'
    }),422

  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      'success':False,
      'error':500,
      'message':'Internal server error'
    }),500

  @app.errorhandler(AuthError)
  def auth_error(err_metadata):
    return jsonify({
      'success':False,
      'error':err_metadata.status_code,
      'message':err_metadata.error['description']
    }),err_metadata.status_code


  return app


# if __name__ == '__main__':
#     APP.run(host='0.0.0.0', port=8080, debug=True)