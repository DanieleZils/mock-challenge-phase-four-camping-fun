from flask import Flask, request, make_response, jsonify
from sqlalchemy.exc import IntegrityError
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Camper, Activity, Signup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


# class Scientists(Resource):

#     def get(self):
#         scientists = Scientist.query.all()
#         scientists_dict_list = [scientist.to_dict()
#                                 for scientist in scientists]
#         response = make_response(
#             scientists_dict_list,
#             200
#         )

#         return response

class Campers(Resource):

    def get(self):
        campers = Camper.query.all()
        campers_dict_list = [camper.to_dict() for camper in campers]
        response = make_response(
            campers_dict_list,
            200
        )
        return response
    
    def post( self ):
        data = request.get_json()

        try:
            new_camper = Camper( name = data['name'], age = data['age'] )
        except ValueError:
            return make_response( { 'error': 'name already taken' }, 400 )
    
        try:
            db.session.add( new_camper )
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return make_response( {'error': 'username or age is invalid'}, 400 )
        return make_response( new_camper.to_dict(), 201 )

api.add_resource(Campers, '/campers')


class CamperById(Resource):

    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return make_response( {'error': 'Camper not found'}, 404 )
        response = make_response( camper.to_dict(rules=('activities',)), 200)

        return response

api.add_resource(CamperById, '/campers/<int:id>')


class Activities(Resource):

    def get(self):
        activities = Activity.query.all()
        activity_dict = [activity.to_dict() for activity in activities]

        response = make_response(activity_dict, 200)

        return response
    
api.add_resource(Activities, '/activities')


class ActivitiesById(Resource):

    def delete(self, id):

        activity = Activity.query.filter_by(id=id).first()
        if not activity:
            return make_response({"error": "Activity not found"}, 404)
        
        try:
            db.session.delete(activity)
            db.session.commit()
        except Exception as e:
            return make_response({
                    "errors": [e.__str__()]
                },
                422
            )
        return make_response ('', 200)
    
api.add_resource(ActivitiesById, '/activities/<int:id>')

class Signups(Resource):
    def post(self):
        data = request.get_json()
        try:
            signup = Signup(
                time=data["time"],
                camper_id=data["camper_id"],
                activity_id=data["activity_id"]
            )
            db.session.add(signup)
            db.session.commit()
            
        except Exception as e:
            response_dict = {
                "errors": [e.__str__()]
            }
            return make_response(
                response_dict,
                422
            )
        response = make_response(
            signup.activity.to_dict(),
            201
        )
        return response


api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
