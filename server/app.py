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

class CamperByResource(Resource):
    def get(self):
        camper_list = [camper.to_dict(rules = ('-signups',)) for camper in Camper.query.all()]
        return camper_list, 200
    
    def post(self):
        data = request.get_json()
        try:
            new_camper = Camper(
                name = data["name"],
                age = data["age"]
            )
            db.session.add(new_camper)
            db.session.commit()
        except ValueError as e:
            print(e.__str__())
            return {"errors": "Post needs name and age"}, 400
        return new_camper.to_dict(), 201
        
api.add_resource(CamperByResource, "/campers")

class CamperById(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id = id).first()
        if not camper:
            return {"error": "Camper not found"}, 404
        return camper.to_dict(), 200
    
    def patch(self, id):
        camper = Camper.query.filter_by(id = id).first()
        if not camper:
            return {"error": "Camper not found"}, 404

        try:
            data = request.get_json()
            for key in data:
                setattr(camper, key, data[key])
            db.session.commit()
        
        except ValueError as e:
            print(e.__str__())
            return {"errors": ["validation errors"]}, 400
        
        return camper.to_dict(), 202
    
api.add_resource(CamperById, "/campers/<int:id>")

class ActivityResource(Resource):
    def get(self):
        activity_list = [activity.to_dict() for activity in Activity.query.all()]
        return activity_list, 200
    
api.add_resource(ActivityResource, "/activities")

class ActivityById(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id = id).first()
        if not activity:
            return {"error": "Activity not found"}, 404

        db.session.delete(activity)
        db.session.commit()

        return "", 204
    
api.add_resource(ActivityById, "/activities/<int:id>")

class SignupResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_signup = Signup(
                camper_id = data["camper_id"],
                activity_id = data["activity_id"],
                time = data["time"]
            )
            db.session.add(new_signup)
            db.session.commit()
        except ValueError as e:
            print(e.__str__())
            return {"errors": ["validation errors"]}, 400
        
        return new_signup.to_dict(), 201
    
api.add_resource(SignupResource, "/signups")

if __name__ == '__main__':
    app.run(port=5555, debug=True)
