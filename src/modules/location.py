
#from database import *

#MY STUFF
from helpers import *

import googlemaps
config = importYaml('configs/config')
gmaps = googlemaps.Client(key=config['keys'][0])

import os


#class Location(Base): as a db class
class Location:

    #SETUP TABLE COLUMNS 
    #SQLALCHEMY
    #__tablename__ = 'location'
    #id    = Column(types.Integer, primary_key=True)
    #name  = Column(types.String(256))
    #north = Column(types.Float(precision=32))
    #south = Column(types.Float(precision=32))
    #east  = Column(types.Float(precision=32))
    #west  = Column(types.Float(precision=32))
    #grids = relationship("Grid")
    #END TABLE SETUP


    #define a location
    def __init__(self, name, north, south, east, west):
        self.name  = name
        self.north = north
        self.south = south
        self.east  = east
        self.west  = west

        self.setup()

    def __repr__(self):
        #return self.serialize()
        return '%s: n: %s, s: %s, e: %s, w: %s' % (self.name, self.north, self.south, self.east, self.west)


    def __str__(self):
        return '%s: n: %s, s: %s, e: %s, w: %s' % (self.name, self.north, self.south, self.east, self.west)

    def setup(self):
        self.root = 'Locations/%s/' % self.name
        #self.root = self.root.replace(' ', '\\ ')
        self.configFile = self.root + 'config'
        self.rawdir      = self.root + 'raw/'
        self.maptilesdir = self.root + 'maptiles/'
        self.slicesdir   = self.root + 'slices/'
        self.vectorsdir  = self.root + 'vectors/'
        self.heightsdir  = self.root + 'heightmaps/'
        self.rezdir      = self.root + 'resolutions/'
        self.tiff        = 'SRTM.tiff'
        self.contours    = 'contours'
        self.tiffFile    = self.root + self.tiff
        self.contoursdir = self.root + self.contours + '/'

        ensure_dir(self.root)
        self.save()




    def save(self):
        #db.add(self)
        #db.commit()
        self.toYaml(self.configFile)

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

    #deprecated
    def toYamlDb(self):
        toYaml('locations')

    #deprecated
    def toYaml(self, filename):
        #locations[sel] = self.serialize()
        saveYaml(self.serialize(), filename)


#return a location from a name
def locationFromName(locChoice):
    #check if the choice is already a location
    if checkExistingLocations(locChoice):
        return locationFromYaml(importYaml('Locations/%s/config' % locChoice))

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

def checkExistingLocations(name):
    locations = os.listdir('Locations')
    if name in locations:
        return True
    return False

def locationFromYaml(YamlLocation):
    name  = YamlLocation['name']
    north = YamlLocation['north']
    south = YamlLocation['south']
    east  = YamlLocation['east']
    west  = YamlLocation['west']
    return Location(name, north, south, east, west)

