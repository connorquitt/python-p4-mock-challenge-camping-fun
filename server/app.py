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


@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET', 'POST'])
def campers():
    if request.method == 'GET':
        campers = Camper.query.all()
        return make_response(
            jsonify([camper.to_dict() for camper in campers]),
            200
        )
    elif request.method == 'POST':
        data = request.get_json()
        
        try:
            new_camper = Camper(
            name = data.get('name'),
            age = data.get('age'),
            )
            db.session.add(new_camper)
            db.session.commit()
            return make_response(new_camper.to_dict(), 201)
        except:
            message_body = {
                "errors": "errors"
            }
            return (make_response(message_body, 400))

@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def campers_by_id(id):

    camper = Camper.query.filter(Camper.id == id).first()

    if not camper:
        return (jsonify({'error': 'Camper not found'}), 404)

    if request.method == 'GET':
        camper_data = {
            'id': camper.id,
            'name': camper.name,
            'age': camper.age,
            'signups': [{'id': signup.id, 'activity_id': signup.activity_id, 'time': signup.time} for signup in camper.signups]
        }

        return make_response(jsonify(camper_data), 200)
    
    elif request.method == 'PATCH':
        data = request.get_json()

        try:
            if 'name' in data:
                camper.name = data['name']
            if 'age' in data:
                camper.age = data['age']
            db.session.add(camper)
            db.session.commit()
        except:
            message_body = {
                "errors": ['validation errors']
            }
            return (make_response(message_body, 400))
        
        return make_response(camper.to_dict(), 202)
    
@app.route('/activities', methods=['GET'])
def activities():
    if request.method == 'GET':
        activities = Activity.query.all()
        return make_response(jsonify([activity.to_dict() for activity in activities]), 200)


@app.route('/activities/<int:id>', methods=['GET', 'DELETE'])
def activities_by_id(id):
    activity = Activity.query.filter(Activity.id == id).first()

    if not activity:
        message_body = {
            'error': 'Activity not found'
        }

        return make_response(message_body, 404)

    if request.method == 'GET':
        return make_response(activity.to_dict(), 200)
    elif request.method == 'DELETE':
        db.session.delete(activity)
        db.session.commit()
        
        response_body = {
            'delete_successful': True,
            'message': 'Activity deleted'
        }
        return make_response(response_body, 204)


@app.route('/signups', methods=['POST'])
def signups():
    if request.method == 'GET':
        signups = Signup.query.all()
        return make_response(jsonify([signup.to_dict() for signup in signups]))
    elif request.method == 'POST':
        data = request.get_json()
        try:
            new_signup = Signup(
            time = data.get('time'),
            camper_id = data.get('camper_id'),
            activity_id = data.get('activity_id')
            )
            db.session.add(new_signup)
            db.session.commit()
        except:
            message_body = {'errors' : ['validation errors']}
            return make_response(message_body, 400)

        return make_response(new_signup.to_dict(), 201)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
