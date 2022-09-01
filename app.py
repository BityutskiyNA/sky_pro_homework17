# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

from create_data import data_create

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)
movie_ns = api.namespace("movie")
director_ns = api.namespace("director")
genre_ns = api.namespace("genre")


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


@movie_ns.route("")
class Movie_all(Resource):
    def get(self):
        return movies_schema.dumps(Movie.query.all())


@movie_ns.route("/<int:n_id>")
class Movie_one(Resource):
    def get(self, n_id):
        return movie_schema.dump(Movie.query.get(n_id))


@movie_ns.route("/")
class Movie_one_by_filter(Resource):
    def get(self):
        director_id = ""
        genre_id = ""
        for x in request.args:
            if x == "director_id":
                director_id = request.args[x]
            elif x == "genre_id":
                genre_id = request.args[x]
        if len(request.args) == 1:
            if director_id == "":
                s = movies_schema.dumps(Movie.query.filter_by(genre_id=genre_id).all())
            elif genre_id == "":
                s = movies_schema.dumps(Movie.query.filter_by(director_id=director_id).all())
        elif len(request.args) == 2:
            s = movies_schema.dumps(Movie.query.filter_by(director_id=director_id, genre_id=genre_id).all())
        return s


@director_ns.route("/<int:d_id>")
class Director_one(Resource):
    def post(self, d_id):
        director = Director.query.get(d_id)
        if not director:
            regjson = request.json
            rez = genre_schema.load(regjson)
            role = Director(**rez)
            with db.session.begin():
                db.session.add(role)
            return "", 204

        return "Элемент с таким id есть в базе", 404

    def put(self, d_id):
        director = Director.query.get(d_id)
        if not director:
            return "", 404
        req_json = request.json
        director.id = req_json.get("id")
        director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "", 204

    def delete(self, d_id):
        director = Director.query.get(d_id)
        if not director:
            return "", 404
        db.session.delete(director)
        db.session.commit()
        return "", 204


@genre_ns.route("/<int:g_id>")
class Genre_one(Resource):
    def post(self, g_id):
        genre = Genre.query.get(g_id)
        if not genre:
            regjson = request.json
            rez = genre_schema.load(regjson)
            role = Genre(**rez)
            with db.session.begin():
                db.session.add(role)
            return "", 204

        return "Элемент с таким id есть в базе", 404

    def put(self, g_id):
        genre = Genre.query.get(g_id)
        if not genre:
            return "", 404
        req_json = request.json
        genre.id = req_json.get("id")
        genre.name = req_json.get("name")
        db.session.add(genre)
        db.session.commit()
        return "", 204

    def delete(self, g_id):
        genre = Genre.query.get(g_id)
        if not genre:
            return "", 404
        db.session.delete(genre)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    data_create()
    app.run(debug=True)
