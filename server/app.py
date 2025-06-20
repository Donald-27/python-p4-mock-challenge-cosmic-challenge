#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Scientist, Mission, Planet

import os

# Flask setup
app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI") or f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

@app.route('/')
def home():
    return ''

# ROUTES & RESOURCES

class Scientists(Resource):
    def get(self):
        scientists = Scientist.query.all()
        return [s.to_dict(rules=('-missions',)) for s in scientists], 200

    def post(self):
        data = request.get_json()
        try:
            new_scientist = Scientist(
                name=data['name'],
                field_of_study=data['field_of_study']
            )
            db.session.add(new_scientist)
            db.session.commit()
            return new_scientist.to_dict(), 201
        except Exception:
            return {'errors': ['validation errors']}, 400


class ScientistByID(Resource):
    def get(self, id):
        s = Scientist.query.get(id)
        if not s:
            return {'error': 'Scientist not found'}, 404
        return s.to_dict(), 200

    def patch(self, id):
        s = Scientist.query.get(id)
        if not s:
            return {'error': 'Scientist not found'}, 404

        data = request.get_json()
        try:
            for attr in data:
                setattr(s, attr, data[attr])
            db.session.commit()
            return s.to_dict(), 202
        except:
            return {'errors': ['validation errors']}, 400

    def delete(self, id):
        s = Scientist.query.get(id)
        if not s:
            return {'error': 'Scientist not found'}, 404
        db.session.delete(s)
        db.session.commit()
        return '', 204


class Planets(Resource):
    def get(self):
        planets = Planet.query.all()
        return [p.to_dict(rules=('-missions',)) for p in planets], 200


class Missions(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_mission = Mission(
                name=data['name'],
                scientist_id=data['scientist_id'],
                planet_id=data['planet_id']
            )
            db.session.add(new_mission)
            db.session.commit()
            return new_mission.to_dict(), 201
        except:
            return {'errors': ['validation errors']}, 400


# ROUTE REGISTRATION
api.add_resource(Scientists, '/scientists')
api.add_resource(ScientistByID, '/scientists/<int:id>')
api.add_resource(Planets, '/planets')
api.add_resource(Missions, '/missions')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
