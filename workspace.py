from helpers import importYaml
import requests
import googlemaps
from GooMPy import GooMPy

styles    = importYaml('styles')
config    = importYaml('config')
locations = importYaml('locations')

keyNum = 0
_KEY = config['keys'][keyNum]

options = config['mapOptions']
staticMapUrl = config['urls']['staticMap']
blankStyle = config['blankStyle']

gmaps = googlemaps.Client(key=config['keys'][0])

isoStyles = {}

def isolateFeature(feature):
    out = [blankStyle]

    for style in styles:
        if style['featureType'] == feature:
            style['hue'] = '#ffffff'
            style['visibility'] = 'on'
            out.append(style)
    return out

for style in styles:
    isoStyles[style['featureType']] = isolateFeature(style['featureType'])

#queryString = staticMapUrl+'?'+objectToString(options, '=', '&')+'&'+stylesToString(styles)+'&key='+config['keys'][keyNum]


#for style in styles:
#    style['lightness'] = 50
#    style['saturation'] = 100


#style = styles[0]

#print(styleString(style))

loc = locations['vi']
north = loc['bounds']['north']
south = loc['bounds']['south']
east = loc['bounds']['east']
west = loc['bounds']['west']
center = {}
heightDeg = loc['bounds']['north']-loc['bounds']['south']
widthDeg = loc['bounds']['west']-loc['bounds']['east']
center['lng'] = loc['bounds']['south']+((heightDeg)/2)
center['lat'] = loc['bounds']['west']+((widthDeg)/2)

import math
import PIL.Image
import cStringIO
import urllib
import os
import time
from hashlib import md5

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.debug('This is a log message.')

#my stuff
#TODO put in a function to allow edit in window
from helpers import *
OPTIONS = importYaml('config')
STYLES = importYaml('styles')
_STYLE_STRING = stylesToString(STYLES)
#logging.debug('style string: '+_STYLE_STRING)


_EARTHPIX = 268435456  # Number of pixels in half the earth's circumference at zoom = 21
_DEGREE_PRECISION = 4  # Number of decimal places for rounding coordinates
_TILESIZE = 640        # Larget tile we can grab without paying
_GRABRATE = 4          # Fastest rate at which we can download tiles without paying

_pixrad = _EARTHPIX / math.pi #the radius of a pixel
 
def _new_image(width, height):

    return PIL.Image.new('RGB', (width, height))

def _roundto(value, digits):

    return int(value * 10**digits) / 10.**digits

def _pixels_to_degrees(pixels, zoom):
    return pixels * 2 ** (21 - zoom)

def _grab_tile(lat, lon, zoom, maptype, _TILESIZE, sleeptime):


    urlbase = 'https://maps.googleapis.com/maps/api/staticmap?center=%f,%f&zoom=%d&maptype=%s&size=%dx%d'
    urlbase +="&"+_STYLE_STRING
    urlbase += _KEY

    #logging.debug('in grabtile: '+_STYLE_STRING)

    specs = lat, lon, zoom, maptype, _TILESIZE, _TILESIZE

    name = md5(('%f_%f_%d_%s_%d_%d' % specs) + _STYLE_STRING).hexdigest()

    filename = 'mapscache/' + name + '.png'

    tile = None

    if os.path.isfile(filename):
        tile = PIL.Image.open(filename)

    else:
        url = urlbase % specs

        result = urllib.urlopen(url).read()
        tile = PIL.Image.open(cStringIO.StringIO(result))
        if not os.path.exists('mapscache'):
            os.mkdir('mapscache')
        tile.save(filename)
        time.sleep(sleeptime) # Choke back speed to avoid maxing out limit

    return tile


def _pix_to_lon(j, lonpix, ntiles, _TILESIZE, zoom):

    return math.degrees((lonpix + _pixels_to_degrees(((j)-ntiles/2)*_TILESIZE, zoom) - _EARTHPIX) / _pixrad)

def _pix_to_lat(k, latpix, ntiles, _TILESIZE, zoom):

    return math.degrees(math.pi/2 - 2 * math.atan(math.exp(((latpix + _pixels_to_degrees((k-ntiles/2)*_TILESIZE, zoom)) - _EARTHPIX) / _pixrad))) 

def fetchTiles(latitude, longitude, zoom, maptype, radius_meters=None, default_ntiles=4):
    '''
    Fetches tiles from GoogleMaps at the specified coordinates, zoom level (0-22), and map type ('roadmap', 
    'terrain', 'satellite', or 'hybrid').  The value of radius_meters deteremines the number of tiles that will be 
    fetched; if it is unspecified, the number defaults to default_ntiles.  Tiles are stored as png images 
    in the mapscache folder.
    '''
 
    latitude = _roundto(latitude, _DEGREE_PRECISION)
    longitude = _roundto(longitude, _DEGREE_PRECISION)

    # https://groups.google.com/forum/#!topic/google-maps-js-api-v3/hDRO4oHVSeM
    pixels_per_meter = 2**zoom / (156543.03392 * math.cos(math.radians(latitude)))

    # number of tiles required to go from center latitude to desired radius in meters
    ntiles = default_ntiles if radius_meters is None else int(round(2 * pixels_per_meter / (_TILESIZE /2./ radius_meters))) 

    lonpix = _EARTHPIX + longitude * math.radians(_pixrad)

    sinlat = math.sin(math.radians(latitude))
    latpix = _EARTHPIX - _pixrad * math.log((1 + sinlat)/(1 - sinlat)) / 2

    bigsize = ntiles * _TILESIZE
    bigimage = _new_image(bigsize, bigsize)

    for j in range(ntiles):
        lon = _pix_to_lon(j, lonpix, ntiles, _TILESIZE, zoom)
        for k in range(ntiles):
            lat = _pix_to_lat(k, latpix, ntiles, _TILESIZE, zoom)
            tile = _grab_tile(lat, lon, zoom, maptype, _TILESIZE, 1./_GRABRATE)
            bigimage.paste(tile, (j*_TILESIZE,k*_TILESIZE))

    west = _pix_to_lon(0, lonpix, ntiles, _TILESIZE, zoom)
    east = _pix_to_lon(ntiles-1, lonpix, ntiles, _TILESIZE, zoom)

    north = _pix_to_lat(0, latpix, ntiles, _TILESIZE, zoom)
    south = _pix_to_lat(ntiles-1, latpix, ntiles, _TILESIZE, zoom)

    return bigimage, (north,west), (south,east)

def fetchArea(north, south, east, west, zoom, maptype):
    latitude  = south+((north-south)/2)
    longitude = west+((west-east)/2)

    pixels_per_meter = 2**zoom / (156543.03392 * math.cos(math.radians(latitude)))


    lonpix = _EARTHPIX + longitude * math.radians(_pixrad)

    sinlat = math.sin(math.radians(latitude))
    latpix = _EARTHPIX - _pixrad * math.log((1 + sinlat)/(1 - sinlat)) / 2




latitude  = center['lat']
longitude = center['lng']
zoom = 4

from geopy.distance import vincenty
topDist = vincenty((north,east), (north, west)).meters
print(topDist)

pixels_per_meter = 2**zoom / (156543.03392 * math.cos(math.radians(latitude)))


lonpix = _EARTHPIX + longitude * math.radians(_pixrad)

sinlat = math.sin(math.radians(latitude))
latpix = _EARTHPIX - _pixrad * math.log((1 + sinlat)/(1 - sinlat)) / 2



