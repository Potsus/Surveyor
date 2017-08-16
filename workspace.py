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

styles    = importYaml('styles')
config    = importYaml('config')
locations = importYaml('locations')

keyNum = 0
_KEY = config['keys'][keyNum]

options = config['mapOptions']
staticMapUrl = config['urls']['staticMap']
blankStyle = config['blankStyle']

OPTIONS = importYaml('config')
STYLES = importYaml('styles')
_STYLE_STRING = stylesToString(STYLES)

_EARTHPIX = 268435456  # Number of pixels in half the earth's circumference at zoom = 21
_DEGREE_PRECISION = 4  # Number of decimal places for rounding coordinates
_TILESIZE = 640        # Larget tile we can grab without paying
_GRABRATE = 2          # Fastest rate at which we can download tiles without paying

_pixrad = _EARTHPIX / math.pi #the radius of a pixel

#gmaps = googlemaps.Client(key=config['keys'][0])
#
#isoStyles = {}
#
#def isolateFeature(feature):
#    out = [blankStyle]
#
#    for style in styles:
#        if style['featureType'] == feature:
#            style['hue'] = '#ffffff'
#            style['visibility'] = 'on'
#            out.append(style)
#    return out
#
#for style in styles:
#    isoStyles[style['featureType']] = isolateFeature(style['featureType'])


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

zoom = 17 #ideal zoom
#zoom = 14

path = 'Locations/%s/' % loc['name']
filename = path + '%s zoom'

 
def _new_image(width, height):

    return PIL.Image.new('RGB', (width, height))

def _roundto(value, digits):

    return int(value * 10**digits) / 10.**digits

def _pixels_to_degrees(pixels, zoom):
    return pixels * 2 ** (21 - zoom)

def getTile(lat, lon, zoom, _TILESIZE, sleeptime):
    #print('grabbing %s, %s' % (lat, lon))


    urlbase = 'https://maps.googleapis.com/maps/api/staticmap?center=%f,%f&zoom=%d&maptype=%s&size=%dx%d'
    urlbase +="&"+_STYLE_STRING
    urlbase += _KEY

    maptype = 'roadmap'

    specs = lat, lon, zoom, maptype, _TILESIZE, _TILESIZE

    name = md5(('%f_%f_%d_%s_%d_%d' % specs) + _STYLE_STRING).hexdigest()

    filename = path + 'maptiles/' + name + '.png'

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

def fetchArea(north, south, east, west, zoom, maptype):

    print('creating image size %sx%s' % (pixwid, pixhigh))
    if yn() == False:
        exit()
    bigimage = _new_image(pixwid, pixhigh)

    print('starting retrieval')
    for i in range(wtiles):
        curLng = (east + (i * wstep) + wstep)
        for j in range(htiles):
            curLat = (north + (j * hstep) + hstep)
            print('getting tile %sx%s' % (i,j))
            tile = getTile(curLat, curLng, zoom, _TILESIZE, 1./_GRABRATE)
            bigimage.paste(tile, (i*_TILESIZE,j*(_TILESIZE-cropFactor)))

    bigimage.save(filename + '.png')


latitude  = center['lat']
longitude = center['lng']
#i think this should be the right zoom for all the features i want

print('calculating stuff')
from geopy.distance import vincenty
topDist = vincenty((north,east), (north, west)).meters
leftDist = vincenty((north,east), (south, east)).meters
radius_meters = topDist

print(topDist)

def getZoom():
    quality = raw_input('pick a zoom level 17 is our ideal ')
    if canCastToInt(quality) == False:
        print("couldn't get a number there, defaulting to 19")
        quality = 19
    else: quality = int(quality)
    return quality

def setZoom():
    global zoom
    zoom = getZoom()

    pixels_per_meter = 2**zoom / (156543.03392 * math.cos(math.radians(latitude)))

    lonpix = _EARTHPIX + longitude * math.radians(_pixrad)

    sinlat = math.sin(math.radians(latitude))
    latpix = _EARTHPIX - _pixrad * math.log((1 + sinlat)/(1 - sinlat)) / 2

    ntiles = int(round(2 * pixels_per_meter / (_TILESIZE /2./ radius_meters)))

    pixwid = math.ceil(topDist/pixels_per_meter)
    pixhigh = math.ceil(leftDist/pixels_per_meter)

    #we need to lose the bottom 22 pixels to cut out the google logo

    wtiles = math.ceil(pixwid/_TILESIZE)
    htiles = math.ceil(pixhigh/(_TILESIZE-22))

    print('image would be %spx by %spx' % (pixwid, pixhigh))
    print('%s tiles by %s tiles' % (wtiles, htiles))
    print('we would need to make %s requests per feature' % (wtiles * htiles))
    print('est time to completion ~%s' % ((wtiles * htiles)/(_GRABRATE/2)))

    print('sample %s at %s by %s?' % (loc['name'], wtiles, htiles))
    if yn() == False:
        zoom = getZoom()
    return zoom

zoom = setZoom()

fetchArea(north, south, east, west, zoom, 'roadmap')



