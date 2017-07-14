import googlemaps
from time import sleep
from datetime import datetime
import requests
from PIL import Image
import PIL.ImageOps
from io import BytesIO
import json
import numpy as np
import os.path

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug('starting surveyor')

#goompy stuff
#from Tkinter import Tk, Canvas, Label, Frame, IntVar, Radiobutton, Button
#from PIL import ImageTk
#from goompy import GooMPy

#my stuff
from helpers import *
from keys import gmapsApiKeys

from calculate import TICK as softTick
from calculate import NORTH, SOUTH, EAST, WEST
TICK = softTick * 32

gmaps = googlemaps.Client(key=gmapsApiKeys[0])
keyNum = 0
options = importJson('options.json')
MAP_RESOLUTION = 320
SCALE = 2

staticMapUrl = "https://maps.googleapis.com/maps/api/staticmap"
ELEVATION_URL = 'https://maps.googleapis.com/maps/api/elevation/json'

#move the styles into a seperate list
styles = options.pop('styles')

# Geocoding an address
LOCATION = 'virgin islands'
geocode_result = gmaps.geocode(LOCATION)

lat = geocode_result[0]['geometry']['location']['lat']
lng = geocode_result[0]['geometry']['location']['lng']

#bounds   = geocode_result[0]['geometry']['bounds']
viewport = geocode_result[0]['geometry']['viewport']

#NORTH = viewport['northeast']['lat'] 
#EAST  = viewport['northeast']['lng']  
#SOUTH = viewport['southwest']['lat'] 
#WEST  = viewport['southwest']['lng'] 

#ELEVATION_RESOLUTION = (MAP_RESOLUTION * SCALE)/4
MAX_REQUESTS = 512
ELEVATION_RESOLUTION = abs(NORTH - SOUTH) / TICK

ELEVATION_RESOLUTION = roundToEven(ELEVATION_RESOLUTION)

def ticksToResolution(a,b):
    return roundToEven(abs(a - b) / TICK)

yResolution = ticksToResolution(NORTH, SOUTH)
xResolution = ticksToResolution(EAST, WEST)

print('fetching grid sized %s x %s is this ok?' % (xResolution, yResolution))
#sleep(4)

elevationGrid = []

junkSample = json.loads('{"elevation": 0, "location": {"lat": 0, "lng": 0}, "resolution": 0}')


filename = '%s at %sx%s' % (geocode_result[0]['address_components'][0]['short_name'], xResolution, yResolution)
#filename = '%s, %s at %s' % (lat, lng, ELEVATION_RESOLUTION)

#def useNextKey():
#    global keyNum
#    if (keynum < len(gmapsApiKeys))
#        keyNum += 1
#        return true
#    return false

def useNextKey():
    global keyNum
    keyNum += 1

def makeJunkData(samples):
    junkData = []
    for i in range(0, samples):
        junkData.append(junkSample)
    return junkData


def requestLineFragment(lineLat, samples, start):
    #if we've run out of keys return junk data
    if (keyNum >= len(gmapsApiKeys)):
        return makeJunkData(samples)

    lineLng = EAST - (TICK * start)

    queryString  = "%s?path=%s,%s|%s,%s&samples=%s&key=%s" % (ELEVATION_URL, lineLat, lineLng, lineLat, lineLng - (TICK * samples), samples, gmapsApiKeys[keyNum])
    response     = requests.get(queryString)
    responseData = json.loads(response.content)
    if responseData['status'] != 'OK':
        logging.debug('response error: %s' % responseData['status'])
        useNextKey()
        return requestLineFragment(lineLat, samples, start)

    return responseData['results']


def getFragmentSamples(desiredSamples):
    if desiredSamples > MAX_REQUESTS:
        return getFragmentSamples(desiredSamples/2)
    return desiredSamples






if os.path.isfile('raw/' + filename + '.json'):
    elevationGrid = importJson('raw/' + filename + '.json')
else:

    #break 
    maxSamples = getFragmentSamples(xResolution)

    for y in range (0, yResolution):

        sampleLat    = NORTH - (TICK * y)
        x = 0
        line = []
        while(x < xResolution):
            #make sure you don't go past elevation resolution
            samplesToRequest = maxSamples
            if(x + maxSamples > xResolution):
                samplesToRequest = xResolution - x
            line.extend(requestLineFragment(sampleLat, samplesToRequest, x))
            x = x + samplesToRequest
        elevationGrid.append(line)
        logging.debug('completed gridline %s of %s' % (y, yResolution))

    writeJsonToFile(elevationGrid, 'raw/' + filename + '.json')





    #for y in range (0, ELEVATION_RESOLUTION):
    #   sampleLat    = NORTH - (TICK * y)
    #   queryString  = "%s?path=%s,%s|%s,%s&samples=%s&key=%s" % (ELEVATION_URL, sampleLat, EAST, sampleLat, WEST, ELEVATION_RESOLUTION, gmapsApiKeys[keynum])
    #   response     = requests.get(queryString)
    #   responseData = json.loads(response.content)
    #   elevationGrid.append(responseData['results'])
    #   logging.debug('completed gridline %s of %s' % (y, ELEVATION_RESOLUTION))
    #   #sleep(0.25)

    #writeJsonToFile(elevationGrid, 'raw/' + filename + '.json')


cleanedData = np.array(cleanGrid(elevationGrid))
np.save('%s cleaned' % filename, cleanedData)

def clipLowerBound(lowerBound):
    cleanedData = np.clip(cleanedData, lowerBound, cleanedData.max())

#clipLowerBound(cleanedData, -25)

#writeJsonToFile(cleanedData, filename + ' cleaned.json')

def generateImage(data, suffix=''):
    imageData = (255*(data - np.max(data))/-np.ptp(data)).astype(int)

    #generate heightmap
    heightMap = Image.fromarray(imageData.astype('uint8'))
    heightMap = PIL.ImageOps.invert(heightMap)
    heightMap = heightMap.transpose(Image.FLIP_LEFT_RIGHT)
    heightMap.save('heightmaps/' + filename + suffix + '.png')

def generateBoundedImage(data, lower, upper):
    data = np.clip(data, lower, upper)
    suffix = (' %s-%s' % (upper, lower))
    print('generating image with bounds %s' % suffix)
    generateImage(data, suffix)

def generateCuts(data, min, layerHeight):
    for i in range(1, int(math.ceil(((data.max() - min) / layerHeight)))):
        upper = (data.max() - (layerHeight * i-1))
        lower = (data.max() - (layerHeight * i))
        
        generateBoundedImage(data, lower, upper)




generateImage(np.clip(cleanedData, -20, cleanedData.max()))

generateCuts(cleanedData, -25, 50)


#Image.new('L', [ELEVATION_RESOLUTION, ELEVATION_RESOLUTION], color=0)



#boundNELat = geocode_result[0]['geometry']['bounds']['northeast']['lat']
#boundNELng = geocode_result[0]['geometry']['bounds']['northeast']['lng']
#boundSWLat = geocode_result[0]['geometry']['bounds']['southwest']['lat']
#boundSWLng = geocode_result[0]['geometry']['bounds']['southwest']['lng']
#
#viewPortNELat = geocode_result[0]['geometry']['viewport']['northeast']['lat']
#viewPortNELng = geocode_result[0]['geometry']['viewport']['northeast']['lng']
#viewPortSWLat = geocode_result[0]['geometry']['viewport']['southwest']['lat']
#viewPortSWLng = geocode_result[0]['geometry']['viewport']['southwest']['lng']



queryString = staticMapUrl+'?'+objectToString(options, '=', '&')+'&'+stylesToString(styles)+'&key='+gmapsApiKeys[keyNum]

#first shot at a hardcoded url
#response = requests.get('https://maps.googleapis.com/maps/api/staticmap?center=mosquito+island&maptype=terrain&scale=2&size=320x320&style=feature:all|element:labels|visibility:off&style=feature:water|element:geometry.stroke|color:0x000000&key=AIzaSyAu4ptX5HdhsJvuK3gDaSwgIk7PpFRoAUg')

#response = requests.get(queryString)
#picture = Image.open(BytesIO(response.content))

#out = picture.crop((0, 0, 640, 595))

#out.save('out.png')

