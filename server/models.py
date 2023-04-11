from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    age = db.Column(db.Integer, nullable = False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    signups = db.relationship('Signup', backref='camper')
    activities = association_proxy('signups', 'activity')
    serialize_rules = ('-signups', '-created_at',
                       '-updated_at', '-activities.created_at', '-activities.updated_at', '-activities.campers')
    
    @validates('name')
    def validates_name(self, key, value):
        if not value:
            raise ValueError('Name must be provided')
        return value
    
    @validates('age')
    def validates_age(self, key, age):
        if age < 8 or age > 18:
            raise ValueError('Age must be between 8 and 18')
        return age


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    signups = db.relationship('Signup', backref='activity')
    campers = association_proxy('signups', 'camper')

    serialize_rules = ('-signups',
                       '-campers.activities', '-created_at', '-updated_at')


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    time = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())



    serialize_rules = ('-camper.signups', '-activity.signups',
                       '-camper.activities', '-activity.campers', '-created_at', '-updated_at')
    
    @validates('time')
    def validates_time(self, key, time):
        if time < 0 or time > 23:
            raise ValueError('Time must be between 0 and 23')
        return time