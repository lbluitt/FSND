import os
from flask_sqlalchemy import SQLAlchemy
import json


DB_HOST = os.getenv('DB_HOST','localhost:5432')
DB_USER = os.getenv('DB_USER','lbluitt')
DB_PASSWORD = os.getenv('DB_PASSWORD','postgres')
DB_NAME = os.getenv('DB_NAME','casting-agency')
DB_PATH = 'postgresql://{}:{}@{}/{}'.format(DB_USER,DB_PASSWORD,DB_HOST,DB_NAME)
db= SQLAlchemy()
'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''

def setup_db(app,database_path=DB_PATH):
    app.config["SQLALCHEMY_DATABASE_URI"]=database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
    db.app=app
    db.init_app(app)
    db.create_all()

class MovieActor(db.Model):
    __tablename__='MovieActor'
    id=db.Column(db.Integer,primary_key=True)
    movie_id=db.Column(db.Integer,db.ForeignKey('Movie.id'),nullable=False)
    actor_id=db.Column(db.Integer,db.ForeignKey('Actor.id'),nullable=False)

    def __repr__(self):
        return f"<id: {self.id}>"
    

class Movie(db.Model):
    __tablename__='Movie'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String,nullable=False)
    release_date = db.Column(db.DateTime,nullable=False)
    actors=db.relationship('MovieActor',backref=db.backref('movie'),lazy='joined',cascade="all, delete")

    def __repr__(self):
        return f"<id: {self.id} name: {self.title}>"

    def __init__(self,title,release_date):
        self.title=title
        self.release_date=release_date

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id':self.id,
            'title':self.title,
            'release_date':self.release_date
        }

class Actor(db.Model):
    __tablename__='Actor'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,nullable=False)
    gender=db.Column(db.String(1),nullable=False)
    birthdate=db.Column(db.DateTime,nullable=False)
    movies=db.relationship('MovieActor',backref=db.backref('actor'),lazy='joined',cascade="all, delete")

    def __repr__(self):
        return f"<id: {self.id} name: {self.name}>"

    def __init__(self,name,gender,birthdate):
        self.name=name
        self.gender=gender
        self.birthdate=birthdate

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id':self.id,
            'name':self.name,
            'gender':self.gender,
            'birthdate':self.birthdate
        }



