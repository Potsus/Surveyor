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

options = config['mapOptions']
staticMapUrl = config['urls']['staticMap']
blankStyle = config['blankStyle']

OPTIONS = importYaml('config')
styles = importYaml('styles')
styleString = stylesToString(styles)

_EARTHPIX = 268435456  # Number of pixels in half the earth's circumference at zoom = 21
_DEGREE_PRECISION = 4  # Number of decimal places for rounding coordinates
_TILESIZE = 640        # Larget tile we can grab without paying
_GRABRATE = 2          # Fastest rate at which we can download tiles without paying
_pixrad = _EARTHPIX / math.pi

#remove the bottom 22 pixels of each tile
cropFactor = 22
url = config['urls']['staticMap']


class mapper:
    keyNum = 0
    key = config['keys'][keyNum]

    bottomCrop = 22

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

    def calculate(self):
        self.heightDeg = abs(self.north)-abs(self.south)
        self.widthDeg = abs(self.west)-abs(self.east)
        self.center = {}
        self.center['lng'] = self.south+((self.heightDeg)/2)
        self.center['lat'] = self.west+((self.widthDeg)/2)


        self.pixels_per_meter = 2**self.zoom / (156543.03392 * math.cos(math.radians(self.center['lat'])))

        self.lonpix = _EARTHPIX + self.center['lng'] * math.radians(_pixrad)

        self.sinlat = math.sin(math.radians(self.center['lat']))
        self.latpix = _EARTHPIX - _pixrad * math.log((1 + self.sinlat)/(1 - self.sinlat)) / 2

        self.pixwid = int(math.ceil(self.topDist*self.pixels_per_meter))
        self.pixhigh = int(math.ceil(self.leftDist*self.pixels_per_meter))

        #we need to lose the bottom 22 pixels to cut out the google logo

        self.wtiles = int(math.ceil(float(self.pixwid)/_TILESIZE))
        self.htiles = int(math.ceil(float(self.pixhigh)/(_TILESIZE-self.bottomCrop)))

        self.wstep = (self.widthDeg*(((self.wtiles*_TILESIZE)/self.pixels_per_meter)/self.topDist))/(self.wtiles*2)
        self.hstep = (self.heightDeg*(((self.htiles*_TILESIZE)/self.pixels_per_meter)/self.leftDist))/(self.htiles*2)

        print('image would be %spx by %spx' % (self.pixwid, self.pixhigh))
        print('%s tiles by %s tiles' % (self.wtiles, self.htiles))
        print('we would need to make %s requests per feature' % (self.wtiles * self.htiles))
        print('est time to completion ~%s' % ((self.wtiles * self.htiles)/(_GRABRATE/2)))


    def setZoom(self, zoom):
        self.zoom = zoom
        self.calculate()

    def setStyle(self, style):
        self.styleString = stylesToString(style)

    def _pix_to_lon(self, j):
        return math.degrees((self.lonpix + _pixels_to_degrees(((j)-self.wtiles/2)*(_TILESIZE-self.bottomCrop), self.zoom) - _EARTHPIX) / _pixrad)

    def _pix_to_lat(self, k):
        return math.degrees(math.pi/2 - 2 * math.atan(math.exp(((self.latpix + _pixels_to_degrees((k-self.htiles/2)*_TILESIZE, self.zoom)) - _EARTHPIX) / _pixrad))) 

    def fetchArea(self):
        print('creating image size %sx%s' % (self.pixwid, self.pixhigh))
        #if yn() == False:
        #    exit()


        self.bigimage = _new_image(self.pixwid, self.pixhigh)

        print('starting retrieval')
        for i in range(self.wtiles):
            curLng = (self.west + (2*i * self.wstep))
            for j in range(self.htiles):
                curLat = (self.north - (2*j * self.hstep))
                print('getting tile %sx%s at %s, %s' % (i,j, curLat, curLng))
                tile = self.getTile(curLat, curLng)
                self.bigimage.paste(tile, ((i*_TILESIZE)+i*int(self._pix_to_lat(i)),(j*(_TILESIZE-(self.bottomCrop*2)))-j*int(self._pix_to_lon(j))))

        self.bigimage.save(self.path + str(self.zoom) + '.png')

    def getTile(self, lat, lon):
        #print('grabbing %s, %s' % (lat, lon))

        urlbase = url + '?center=%f,%f&zoom=%d&size=%dx%d'
        urlbase +="&" + styleString
        urlbase +=self.key

        maptype = 'roadmap'

        specs = lat, lon, self.zoom+1, _TILESIZE, _TILESIZE

        name = md5(('%f_%f_%d_%d_%d' % specs) + styleString).hexdigest()

        filename = self.path + 'maptiles/' + name + '.png'

        sleeptime = 1./_GRABRATE

        tile = None

        if os.path.isfile(filename):
            tile = PIL.Image.open(filename)

        else:
            uri = urlbase % specs

            result = urllib.urlopen(uri).read()
            tile = PIL.Image.open(cStringIO.StringIO(result))
            if not os.path.exists('mapscache'):
                os.mkdir('mapscache')
            tile.save(filename)
            time.sleep(sleeptime) # Choke back speed to avoid maxing out limit

        return tile

    def invertZoom(self):
        return abs(self.zoom -22)

def _new_image(width, height):

    return PIL.Image.new('RGB', (width, height))

def _roundto(value, digits):

    return int(value * 10**digits) / 10.**digits

def _pixels_to_degrees(pixels, zoom):
    return pixels * 2 ** (21 - zoom)
