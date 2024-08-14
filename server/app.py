#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)


@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        campers = Camper.query.all()
        return [camper.to_dict(only=('id', 'name', 'age')) for camper in campers], 200
    def post(self):
        name = request.get_json()['name']
        age = request.get_json()['age']
        
        try:
            camper = Camper(name=name, age=age)
            db.session.add(camper)
            db.session.commit()
            return camper.to_dict(only=('id', 'name', 'age')), 201
        except:
            return {'errors': ['validation errors']}, 400

class CamperById(Resource):
    def get(self, id):
        camper = Camper.query.filter(Camper.id == id).first()
        if camper:
            return camper.to_dict(), 200
        return {'error': 'Camper not found'}, 404
    def patch(self, id):
        camper = Camper.query.filter(Camper.id == id).first()
        if camper:
            try:
                for attr in request.get_json():
                    setattr(camper, attr, request.get_json()[attr])
                
                db.session.add(camper)
                db.session.commit()

                return camper.to_dict(only=('id', 'name', 'age')), 202
            except:
                return {'errors': ['validation errors']}, 400
        return {'error': 'Camper not found'}, 404

class Activities(Resource):
    def get(self):
        activities = Activity.query.all()
        return [activity.to_dict(only=('id', 'name', 'difficulty')) for activity in activities], 200

class ActivitiesById(Resource):
    def delete(self, id):
        activity = Activity.query.filter(Activity.id == id).first()
        if activity:
            db.session.delete(activity)
            db.session.commit()
            return {}, 204
        return {'error': 'Activity not found'}, 404

class Signups(Resource):
    def post(self):
        time = request.get_json()['time']
        camper_id = request.get_json()['camper_id']
        activity_id = request.get_json()['activity_id']
        try:
            signup = Signup(time=time, camper_id=camper_id, activity_id=activity_id)
            db.session.add(signup)
            db.session.commit()
            return signup.to_dict(), 201
        except:
            return {'errors': ['validation errors']}, 400

api.add_resource(Signups, "/signups")
api.add_resource(Activities, "/activities")
api.add_resource(ActivitiesById, "/activities/<int:id>")
api.add_resource(Campers, "/campers")
api.add_resource(CamperById, "/campers/<int:id>")
if __name__ == '__main__':
    app.run(port=5555, debug=True)
