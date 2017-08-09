#SETUP SQLALCHEMY AND DATABASE
from sqlalchemy import Table, Column, types, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from geoalchemy2 import Geometry
 
Base = declarative_base()

from sqlalchemy import create_engine
engine = create_engine('postgresql://surveyuser:surveyuser@localhost/surveydb')
 
from sqlalchemy.orm import sessionmaker
session = sessionmaker()
session.configure(bind=engine)

#MY STUFF
from helpers import *

import googlemaps
config = importYaml('config')
gmaps = googlemaps.Client(key=config['keys'][0])


class Location(Base):

    #SETUP TABLE COLUMNS
    __tablename__ = 'locations'
    id    = Column(types.Integer, primary_key=True)
    name  = Column(types.String(256))
    north = Column(types.Float(precision=32))
    south = Column(types.Float(precision=32))
    east  = Column(types.Float(precision=32))
    west  = Column(types.Float(precision=32))
    
    #END TABLE SETUP

    #define a location
    def __init__(self, name, north, south, east, west):
        self.name  = name
        self.north = north
        self.south = south
        self.east  = east
        self.west  = west

    def __repr__(self):
        #return self.serialize()
        return '%s: n: %s, s: %s, e: %s, w: %s' % (self.name, self.north, self.south, self.east, self.west)


    def __str__(self):
        return '%s: n: %s, s: %s, e: %s, w: %s' % (self.name, self.north, self.south, self.east, self.west)

    def save(self):
        db.add(self)
        db.commit()

    def serialize(self):
        obj = {}
        obj['name']  = self.name
        obj['north'] = self.north
        obj['south'] = self.south
        obj['east']  = self.east
        obj['west']  = self.west
        return obj

#geolocate a place and return it as a location
def locationFromName(locChoice):
    #geocode our choice
    geocode_result = gmaps.geocode(locChoice)

    #TODO search for existing copy of location
    #self.lookup(geocode_result)

    print('found : ' + geocode_result[0]['address_components'][0]['long_name'])

    name  = geocode_result[0]['address_components'][0]['long_name']
    north = geocode_result[0]['geometry']['viewport']['northeast']['lat']
    south = geocode_result[0]['geometry']['viewport']['southwest']['lat']
    east  = geocode_result[0]['geometry']['viewport']['northeast']['lng']
    west  = geocode_result[0]['geometry']['viewport']['southwest']['lng']
    return Location(name, north, south, east, west)

class Grid(Base):

    #SETUP TABLE COLUMNS
    __tablename__ = 'grids'
    id    = Column(types.Integer, primary_key=True)
    quality = Column(types.Integer)
    #END TABLE SETUP

class Row(Base):

    #SETUP TABLE COLUMNS
    __tablename__ = 'rows'
    id    = Column(types.Integer, primary_key=True)
    
    latitude = Column(types.Float)
    #END TABLE SETUP

class Point(Base):
    #SETUP TABLE COLUMNS
    __tablename__ = 'points'
    id        = Column(types.Integer, primary_key=True)
    point  = Column(Geometry('POINT'))
    elevation = Column(types.Float)
    resolution = Column(types.Float)
    row = Column(types.Integer, ForeignKey('Row.id'))
    #END COLUMN SETUP

    def __repr__(self):
        return '%s' % self.elevation


#map out all relations
Location.grids = relationship("Grid", backref="locations")
Grid.location_id = Column(types.Integer, ForeignKey('locations.id'))
Grid.location = relationship("Location")
Row.grid_id  = Column(types.Integer, ForeignKey('grids.id'))
Row.grid = relationship('grids')

Base.metadata.create_all(engine)

