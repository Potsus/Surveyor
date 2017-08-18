from helpers import *
import requests
import math
from StringIO import StringIO
import cStringIO
import PIL.Image
import urllib
import time
from geopy.distance import vincenty
import utm

styles    = importYaml('styles')
config    = importYaml('config')
locations = importYaml('locations')

STATIC_MAP_URL = config['urls']['staticMap']

EARTHPIX = 268435456  # Number of pixels in half the earth's circumference at zoom = 21
DEGREE_PRECISION = 4  # Number of decimal places for rounding coordinates
TILESIZE = config['mapOptions']['size']        # Larget tile we can grab without paying
GRABRATE = 4          # Fastest rate at which we can download tiles without paying
PIXRAD = EARTHPIX / math.pi
LOGO_CROP = 22 #we need to lose the bottom 22 pixels at scale = 1 to cut out the google logo
SLEEPTIME = 1./GRABRATE


class Mapper:
    keyNum = 0
    keys   = config['keys']
    key    = keys[keyNum]
    errorTile = PIL.Image.open(config['errorImage'])
    errorHash = hash(errorTile.tobytes())

    def __init__(self, name, north, south, east, west):
        self.name = name
        self.north = north
        self.south = south
        self.east  = east 
        self.west  = west

        self.scale = (meterScale(self.north) + meterScale(self.south))/2
        self.topDist  = vincenty((self.north,self.east), (self.north, self.west)).meters
        self.leftDist = vincenty((self.north,self.east), (self.south, self.east)).meters

        self.zoom = config['mapOptions']['zoom']
        self.mapType = config['mapOptions']['mapType']

        self.path = 'Locations/%s/' % self.name
        self.tilesPath = self.path + 'maptiles/' 

        self.styleString = stylesToString(styles['default'])


        self.calculate() #old method, lines up right but result is no good
        #self.betterCalc()
        self.updateUrlBase()

    def setZoom(self, zoom):
        self.zoom = zoom
        self.calculate()
        #self.betterCalc()

    def setStyle(self, style):
        self.styleString = stylesToString(style)
        self.updateUrlBase()

    def setMapType(self, mapType):
        if locInList(mapType, config['mapTypes']):
            self.mapType = mapType
            self.updateUrlBase()

    def useNextKey():
        self.keyNum += 1
        self.key = keys[self.keyNum]

    def updateUrlBase(self):
        self.urlbase  = STATIC_MAP_URL + '?center=%f,%f&zoom=%d&size=%dx%d'
        if self.mapType != 'roadmap':
            self.urlbase += "&maptype=" + self.mapType
        if self.styleString != '':
            self.urlbase += "&" + self.styleString
        self.urlbase += "&key=" + self.key


    def getTile(self, lat, lon):
        if self.keyNum >= len(self.keys):
            print('ran out of keys, filling with junk')
            return errorTile #we're out of keys for today, return the error image before we make another request

        specs = lat, lon, self.zoom+1, TILESIZE, TILESIZE
        name = hash(('%f_%f_%d_%d_%d' % specs) + self.styleString)
        filename = self.tilesPath + name + '.png'
        
        tile = None
        if config['useCache'] and fileExists(filename):
            #print('found %s' % filename)
            tile = PIL.Image.open(filename)
        else:
            uri = self.urlbase % specs

            result = urllib.urlopen(uri).read()
            tile = PIL.Image.open(cStringIO.StringIO(result))
            ensure_dir('mapscache')

            #if hash(tile) == config['errorHash']:
            if hash(tile.tobytes()) == self.errorHash:
                self.useNextKey()
                return self.getTile(lat, lon)
            tile.save(filename)

        if config['debug'] == True:
            tile = drawCross(tile)

        return tile


    def calculate(self):
        self.heightDeg = abs(self.north)-abs(self.south)
        self.widthDeg = abs(self.west)-abs(self.east)
        self.center = {}
        self.center['lng'] = self.south+((self.heightDeg)/2)
        self.center['lat'] = self.west+((self.widthDeg)/2)
        self.topCorrectDist = self.topDist * (1/self.scale)
        self.leftCorrectDist = self.leftDist * (1/self.scale)

        #TODO: this is only for the lat changes, lon changes might be different?
        self.pixels_per_meter = 2**self.zoom / (156543.03392 * math.cos(math.radians(self.center['lat'])))

        self.lonpix = EARTHPIX + self.center['lng'] * math.radians(PIXRAD)

        self.sinlat = math.sin(math.radians(self.center['lat']))
        self.latpix = EARTHPIX - PIXRAD * math.log((1 + self.sinlat)/(1 - self.sinlat)) / 2

        #TODO: this is close but still wrong 
        self.pixwid = int(math.ceil(self.topDist*self.pixels_per_meter))
        self.pixhigh = int(math.ceil(self.leftDist*self.pixels_per_meter))


        self.wtiles = int(math.ceil(float(self.pixwid)/TILESIZE))
        self.htiles = int(math.ceil(float(self.pixhigh)/(TILESIZE-LOGO_CROP)))

        self.wstep = (self.widthDeg*(((self.wtiles*TILESIZE)/self.pixels_per_meter)/self.topDist))/(self.wtiles*2)
        self.hstep = (self.heightDeg*(((self.htiles*TILESIZE)/self.pixels_per_meter)/self.leftDist))/(self.htiles*2)

        self.pixwid = int(math.ceil(self.topCorrectDist*self.pixels_per_meter))
        self.pixhigh = int(math.ceil(self.leftCorrectDist*self.pixels_per_meter))

        #correct for google's meter/pixel
        self.imgwid  = TILESIZE*self.scale* self.pixels_per_meter
        self.imghigh = (TILESIZE-LOGO_CROP)*self.scale * self.pixels_per_meter

        print('')
        ratio = 6304/float(1982)
        curRatio = self.pixwid/float(self.pixhigh)
        print('IDEAL RATIO: %s' % ratio)
        print(' YOUR RATIO: %s' % curRatio)
        print('Image would be %spx by %spx' % (self.pixwid, self.pixhigh))
        print('%s tiles by %s tiles' % (self.wtiles, self.htiles))
        print('a width step is %s or %s of the total distance' % (self.wstep, 1/(self.widthDeg/self.wstep)))
        print('a height step is %s or %s of the total distance' % (self.hstep, 1/(self.heightDeg/self.hstep)))
        print('vince says its %s by %s meters' % (self.topDist, self.leftDist))
        print('     i say its %s by %s meters' % (self.topCorrectDist, self.leftCorrectDist))
        print('a tile is %s by %s meters ' % (self.imgwid, self.imghigh))
        print('meter scale is ~%s' % self.scale)
        print('')


    def degToLon(i):
        pass

    def _pix_to_lon(self, j):
        return math.degrees((self.lonpix + _pixels_to_degrees( ((j)-self.wtiles/2) * (TILESIZE-LOGO_CROP) , self.zoom) - EARTHPIX) / PIXRAD)

    def _pix_to_lat(self, k):
        return math.degrees(math.pi/2 - 2 * math.atan(math.exp(((self.latpix + _pixels_to_degrees((k-self.htiles/2)*TILESIZE, self.zoom)) - EARTHPIX) / PIXRAD))) 

    def getScale(self, lat):
        return (156543.03392 * math.cos(lat * math.pi / 180) / 2**(self.zoom))

    def pixToMeters(self, pix, lat):
        return (pix * self.getScale(lat)) * meterScale(lat)

    def betterCalc(self):
        #the degree difference between the start point and end point
        self.heightDeg = abs(self.north)- abs(self.south)
        self.widthDeg  = abs(self.west) - abs(self.east)

        self.nw = utm.from_latlon(self.north, self.west)
        self.ne = utm.from_latlon(self.north, self.east)
        self.sw = utm.from_latlon(self.south, self.west)
        self.se = utm.from_latlon(self.south, self.east)

        #average how far off meter calculations are at this lat
        #TODO: recalculate at each step
        self.scale = (meterScale(self.north) + meterScale(self.south))/2

        #average pixels per meter at this lat and zoom
        #TODO: get it for each image
        self.meters_per_pixel = (self.getScale(self.north) + self.getScale(self.south))/2

        #correct for the vincenty difference
        self.topCorrectDist  = self.topDist  * (self.scale)
        self.leftCorrectDist = self.leftDist * (self.scale)

        self.pixwid  = int(math.ceil(self.topCorrectDist))
        self.pixhigh = int(math.ceil(self.leftCorrectDist))

        #correct for google's meter/pixel
        self.imgwid  = (TILESIZE*self.scale)* self.meters_per_pixel
        self.imghigh = (TILESIZE-LOGO_CROP)*(self.scale) * self.meters_per_pixel


        #these only really control if we have enough tiles
        self.wscans = self.pixwid/self.imgwid
        self.hscans = self.pixhigh/self.imghigh

        self.wtiles = int(math.ceil(self.wscans))
        self.htiles = int(math.ceil(self.hscans))


        #get half a step in degrees
        self.wstep = (self.widthDeg  / self.wtiles)/2
        self.hstep = (self.heightDeg / (self.htiles * (self.imghigh/self.imgwid)))/2 #make sure to add in the difference from the crop 

        print('')
        ratio = 6304/float(1982)
        curRatio = self.pixwid/float(self.pixhigh)
        print('IDEAL RATIO: %s' % ratio)
        print(' YOUR RATIO: %s' % curRatio)
        print('Image would be %spx by %spx' % (self.pixwid, self.pixhigh))
        print('%s tiles by %s tiles' % (self.wscans, self.hscans))
        print('a width step is %s or %s of the total distance' % (self.wstep, 1/(self.widthDeg/self.wstep)))
        print('a height step is %s or %s of the total distance' % (self.hstep, 1/(self.heightDeg/self.hstep)))
        print('vince says its %s by %s meters' % (self.topDist, self.leftDist))
        print('     i say its %s by %s meters' % (self.topCorrectDist, self.leftCorrectDist))
        print('a tile is %s by %s meters ' % (self.imgwid, self.imghigh))
        print('')
        #print('We would need to make %s requests per feature' % (self.wtiles * self.htiles))
        #print('Estimated time to completion ~%s' % ((self.wtiles * self.htiles)/(GRABRATE/2)))

    def betterFetch(self):
        print('creating image size %sx%s' % (self.pixwid, self.pixhigh))
        self.bigimage = _new_image(self.pixwid, self.pixhigh)

        print('starting retrieval')
        for i in range(self.wtiles):
            curLng = (self.west + (2 * i * self.wstep) + self.wstep)
            for j in range(self.htiles):
                curLat = (self.north - (2 * j * self.hstep) - self.hstep)
                #print('getting tile %sx%s at %s, %s' % (i,j, curLat, curLng))
                self.tile = self.getTile(curLat, curLng)
                self.bigimage.paste(self.tile, (i*TILESIZE, j*(TILESIZE-LOGO_CROP)))#TODO: move this correction into the step calculations
                time.sleep(SLEEPTIME) # Choke back speed to avoid maxing out limit

        self.bigimage.save(self.path + str(self.zoom) + '.png') #save the finished map



    #TODO: convert this to use cairo to elimimate subpixel error accumulation
    def fetchArea(self):
        print('creating image size %sx%s' % (self.pixwid, self.pixhigh))
        self.bigimage = _new_image( int(math.ceil(self.pixwid + abs(int(round(self._pix_to_lat(self.wtiles/2.))))/self.wtiles)), int(math.ceil(self.pixhigh + abs(int(round(self._pix_to_lon(self.htiles/2.))))/self.htiles)))

        print('starting retrieval')
        for i in range(self.wtiles):
            curLng = (self.west + (2*i * self.wstep) + self.wstep)
            for j in range(self.htiles):
                curLat = (self.north - (2*j * self.hstep) - self.hstep)
                print('getting tile %sx%s at %s, %s' % (i,j, curLat, curLng))
                tile = self.getTile(curLat, curLng)
                time.sleep(SLEEPTIME) # Choke back speed to avoid maxing out limit
                self.bigimage.paste(tile, (
                i*(TILESIZE + int(round(self._pix_to_lat(i)))) #tile size and placement for map to lineup is good
                + int(round(self._pix_to_lat(self.wtiles/2.)/2)), #left adjustment average tile adjustment
                j*(TILESIZE-(LOGO_CROP*2) - int(round(self._pix_to_lon(j)))) #tile size and placement for map to lineup is good
                - int(round(self._pix_to_lon(self.htiles/2.)*2))) #top adjustment 
                ) 

        self.bigimage.save(self.path + str(self.zoom) + '.png') #save the finished map


def meterScale(lat):
    return (1/math.cos(lat))

def utmDist(a,b):
    horiz = abs(a[0] - b[0])
    vert  = abs(a[1] - b[1])
    return (horiz, vert)

def _pixels_to_degrees(pixels, zoom):
    return pixels * 2 ** (21 - zoom)

def _new_image(width, height):

    return PIL.Image.new('RGB', (width, height))

def _roundto(value, digits):

    return int(value * 10**digits) / 10.**digits

