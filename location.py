
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

    def serializeYaml(self):
        obj = {}
        obj['name']  = self.name
        obj['bounds']['north'] = self.north
        obj['bounds']['south'] = self.south
        obj['bounds']['east']  = self.east
        obj['bounds']['west']  = self.west
        return obj

    def deserialize(self, location):
        self.name  = location['name']
        self.north = location['bounds']['north']
        self.south = location['bounds']['south']
        self.east  = location['bounds']['east']
        self.west  = location['bounds']['west']

    #deprecated
    def toYaml(self):
        #locations[sel] = self.serialize()
        saveYaml(self.serialize(), 'locations')



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
