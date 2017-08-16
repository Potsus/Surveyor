from helpers import *
#import requests
#import googlemaps
import math
import PIL.Image
import cStringIO
import urllib
import os
import time
from hashlib import md5
from geopy.distance import vincenty

styles    = importYaml('styles')
config    = importYaml('config')
locations = importYaml('locations')

staticMapUrl = config['urls']['staticMap']
styles = importYaml('styles')

EARTHPIX = 268435456  # Number of pixels in half the earth's circumference at zoom = 21
DEGREE_PRECISION = 4  # Number of decimal places for rounding coordinates
TILESIZE = config['mapOptions']['size']        # Larget tile we can grab without paying
GRABRATE = 4          # Fastest rate at which we can download tiles without paying
PIXRAD = EARTHPIX / math.pi
LOGO_CROP = 22 #we need to lose the bottom 22 pixels at scale = 1 to cut out the google logo
SLEEPTIME = 1./GRABRATE


class mapper:
    keyNum = 0
    keys   = config['keys']
    key    = keys[keyNum]

    def __init__(self, name, north, south, east, west):
        self.name = name
        self.north = north
        self.south = south
        self.east  = east 
        self.west  = west

        self.topDist = vincenty((self.north,self.east), (self.north, self.west)).meters
        self.leftDist = vincenty((self.north,self.east), (self.south, self.east)).meters

        self.zoom = 17

        self.path = 'Locations/%s/' % self.name
        self.tilesPath = self.path + 'maptiles/' 

        self.styleString = stylesToString(styles)

        self.calculate()

    def setZoom(self, zoom):
        self.zoom = zoom
        self.calculate()

    def setStyle(self, style):
        self.styleString = stylesToString(style)

    def next

    def _pix_to_lon(self, j):
        return math.degrees((self.lonpix + _pixels_to_degrees(((j)-self.wtiles/2)*(TILESIZE-LOGO_CROP), self.zoom) - EARTHPIX) / PIXRAD)

    def _pix_to_lat(self, k):
        return math.degrees(math.pi/2 - 2 * math.atan(math.exp(((self.latpix + _pixels_to_degrees((k-self.htiles/2)*TILESIZE, self.zoom)) - EARTHPIX) / PIXRAD))) 

    def calculate(self):
        self.heightDeg = abs(self.north)-abs(self.south)
        self.widthDeg = abs(self.west)-abs(self.east)
        self.center = {}
        self.center['lng'] = self.south+((self.heightDeg)/2)
        self.center['lat'] = self.west+((self.widthDeg)/2)

        #TODO: this is only for the lat changes, lon changes might be different?
        self.pixels_per_meter = 2**self.zoom / (156543.03392 * math.cos(math.radians(self.center['lat'])))

        self.lonpix = EARTHPIX + self.center['lng'] * math.radians(PIXRAD)

        self.sinlat = math.sin(math.radians(self.center['lat']))
        self.latpix = EARTHPIX - PIXRAD * math.log((1 + self.sinlat)/(1 - self.sinlat)) / 2

        self.pixwid = int(math.ceil(self.topDist*self.pixels_per_meter))
        self.pixhigh = int(math.ceil(self.leftDist*self.pixels_per_meter))

        self.wtiles = int(math.ceil(float(self.pixwid)/TILESIZE))
        self.htiles = int(math.ceil(float(self.pixhigh)/(TILESIZE-LOGO_CROP)))

        self.wstep = (self.widthDeg*(((self.wtiles*TILESIZE)/self.pixels_per_meter)/self.topDist))/(self.wtiles*2)
        self.hstep = (self.heightDeg*(((self.htiles*TILESIZE)/self.pixels_per_meter)/self.leftDist))/(self.htiles*2)

        print('image would be %spx by %spx' % (self.pixwid, self.pixhigh))
        print('%s tiles by %s tiles' % (self.wtiles, self.htiles))
        print('we would need to make %s requests per feature' % (self.wtiles * self.htiles))
        print('est time to completion ~%s' % ((self.wtiles * self.htiles)/(GRABRATE/2)))



    def fetchArea(self):
        print('creating image size %sx%s' % (self.pixwid, self.pixhigh))

        self.bigimage = _new_image(self.pixwid, self.pixhigh)

        print('starting retrieval')
        for i in range(self.wtiles):
            curLng = (self.west + (2*i * self.wstep) + self.wstep)
            for j in range(self.htiles):
                curLat = (self.north - (2*j * self.hstep) - self.hstep)
                print('getting tile %sx%s at %s, %s' % (i,j, curLat, curLng))
                tile = self.getTile(curLat, curLng)
                self.bigimage.paste(tile, ((i*TILESIZE)+i*int(self._pix_to_lat(i)),(j*(TILESIZE-(LOGO_CROP*2)))-j*int(self._pix_to_lon(j))))

        self.bigimage.save(self.path + str(self.zoom) + '.png')



    def getTile(self, lat, lon):
        if self.keyNum > 
        #print('grabbing %s, %s' % (lat, lon))

        urlbase = staticMapUrl + '?center=%f,%f&zoom=%d&size=%dx%d'
        urlbase +="&" + self.styleString
        urlbase +=self.key

        maptype = 'roadmap'

        specs = lat, lon, self.zoom+1, TILESIZE, TILESIZE

        name = md5(('%f_%f_%d_%d_%d' % specs) + styleString).hexdigest()

        filename = self.path + 'maptiles/' + name + '.png'

        tile = None

        if config['useCache'] and fileExists(filename):
            tile = PIL.Image.open(filename)

        else:
            uri = urlbase % specs

            result = urllib.urlopen(uri).read()
            tile = PIL.Image.open(cStringIO.StringIO(result))
            ensure_dir('mapscache')

            if hash(tile) != config['errorHash']:
                tile.save(filename)
            else:
                self.nextKey()
                return self.getTile(lat, lon)

            time.sleep(SLEEPTIME) # Choke back speed to avoid maxing out limit

        return tile


def _new_image(width, height):

    return PIL.Image.new('RGB', (width, height))

def _roundto(value, digits):

    return int(value * 10**digits) / 10.**digits

def _pixels_to_degrees(pixels, zoom):
    return pixels * 2 ** (21 - zoom)
