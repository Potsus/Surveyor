
from database import *

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

class Grid(Base):

    #SETUP TABLE COLUMNS
    __tablename__ = 'grids'
    id    = Column(types.Integer, primary_key=True)
    location_id = Column(types.Integer, ForeignKey('Location.id'))
    location = relationship('Location')
    quality = Column(types.Integer)
    #END TABLE SETUP

Location.grids = relationship("Grid", order_by=Grid.id, back_populates="Location")

class Row(Base):

    #SETUP TABLE COLUMNS
    __tablename__ = 'rows'
    id    = Column(types.Integer, primary_key=True)
    grid_id  = Column(types.Integer, ForeignKey('Grid.id'))
    grid = relationship('Grid')
    latitude = Column(types.Float)
    #END TABLE SETUP



