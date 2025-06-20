from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin


convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    distance_from_earth = db.Column(db.Integer, nullable=False)
    nearest_star = db.Column(db.String, nullable=False)

    missions = relationship("Mission", back_populates="planet", cascade="all, delete-orphan")
    scientists = association_proxy("missions", "scientist")

    serialize_rules = ('-missions.planet',)


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    field_of_study = db.Column(db.String, nullable=False)

    missions = relationship("Mission", back_populates="scientist", cascade="all, delete-orphan")
    planets = association_proxy("missions", "planet")

    serialize_rules = ('-missions.scientist',)

    @validates('name', 'field_of_study')
    def validate_fields(self, key, value):
        if not value or value.strip() == '':
            raise ValueError(f"{key} must be provided and non-empty")
        return value


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)

    scientist = relationship("Scientist", back_populates="missions")
    planet = relationship("Planet", back_populates="missions")

    serialize_rules = ('-scientist.missions', '-planet.missions')

    @validates('name', 'scientist_id', 'planet_id')
    def validate_fields(self, key, value):
        if not value:
            raise ValueError(f"{key} must be provided and non-empty")
        return value
