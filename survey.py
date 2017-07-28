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
LOCATION = 'british virgin islands'
geocode_result = gmaps.geocode(LOCATION)

lat = geocode_result[0]['geometry']['location']['lat']
lng = geocode_result[0]['geometry']['location']['lng']

#bounds   = geocode_result[0]['geometry']['bounds']
viewport = geocode_result[0]['geometry']['viewport']

#NORTH = viewport['northeast']['lat'] 
#EAST  = viewport['northeast']['lng']  
#SOUTH = viewport['southwest']['lat'] 
#WEST  = viewport['southwest']['lng'] 

#thousand islands
#NORTH = 44.485782
#EAST  = -75.740578
#SOUTH = 44.183296
#WEST  = -76.204782
#geocode_result[0]['address_components'][0]['short_name'] = 'alex bay'

#filename = '%s at %sx%s' % (geocode_result[0]['address_components'][0]['short_name'], xResolution, yResolution)

#ELEVATION_RESOLUTION = (MAP_RESOLUTION * SCALE)/4
MAX_REQUESTS = 512
ELEVATION_RESOLUTION = abs(NORTH - SOUTH) / TICK

ELEVATION_RESOLUTION = roundToEven(ELEVATION_RESOLUTION)

def ticksToResolution(a,b):
    #no longer needed because resolution doesn't have to devide into even numbers
    #pixels should be sampled in the center of their pixel
    #this will almost never devide evenly 
    #return roundToEven(abs(a - b) / TICK)
    return int(math.ceil(abs(a - b) / TICK))

yResolution = ticksToResolution(NORTH, SOUTH)
xResolution = ticksToResolution(EAST, WEST)



print('fetching grid sized %s x %s is this ok?' % (xResolution, yResolution))
sleep(4)

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

def getFragmentSamples(desiredSamples):
    if desiredSamples > MAX_REQUESTS:
        return getFragmentSamples(desiredSamples/2)
    return int(math.floor(desiredSamples))

def requestLineFragment(lineLat, samples, start):
    #if we've run out of keys return junk data
    if (keyNum >= len(gmapsApiKeys)):
        return makeJunkData(samples)

    lineLng = EAST - (TICK * start)

    queryString  = "%s?path=%s,%s|%s,%s&samples=%s&key=%s" % (ELEVATION_URL, lineLat, lineLng, lineLat, lineLng - (TICK * (samples -1)), samples, gmapsApiKeys[keyNum])
    response     = requests.get(queryString)
    responseData = json.loads(response.content)
    if responseData['status'] != 'OK':
        logging.debug('response error: %s' % responseData['status'])
        useNextKey()
        return requestLineFragment(lineLat, samples, start)

    return responseData['results']



def getLat(point):
    return point['location']['lng']

def getRow(lat):
    x   = 0
    row = []
    while(x < xResolution):
        #make sure you don't go past elevation resolution
        samplesToRequest = MAX_REQUESTS
        if(x + samplesToRequest > xResolution):
            samplesToRequest = xResolution - x
        row.extend(requestLineFragment(lat, samplesToRequest, x))
        x += samplesToRequest
    return row


#START THE THING

useCache = 1

#if i already have data load it
if os.path.isfile('raw/' + filename + '.json') & useCache == 1:
    logging.debug('loading data from file...')
    elevationGrid = importJson('raw/' + filename + '.json')
else:
    #


    #this is inneficent now
    #maxSamples = getFragmentSamples(xResolution)

    for y in range (0, yResolution):

        sampleLat    = NORTH - (TICK * y)
        
        elevationGrid.append(getRow(sampleLat))
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


logging.debug('cleaning data...')
cleanedData = np.array(cleanGrid(elevationGrid))
#np.save('%s cleaned' % filename, cleanedData)

def clipLowerBound(dataArray, lowerBound):
    return np.clip(dataArray, lowerBound, dataArray.max())

#clipLowerBound(cleanedData, -25)

#writeJsonToFile(cleanedData, filename + ' cleaned.json')

def saveAsImage(data, handle):
    imageData = (255*(data - np.max(data))/-np.ptp(data)).astype(int)

    #generate heightmap
    heightMap = Image.fromarray(imageData.astype('uint8'))
    heightMap = PIL.ImageOps.invert(heightMap)
    heightMap = heightMap.transpose(Image.FLIP_LEFT_RIGHT)
    heightMap.save(handle + '.png')

def makeSlice(data, lower, upper):
    data = np.clip(data, lower, upper)
    suffix = (' %s-%s' % (upper, lower))
    print('generating image with bounds %s' % suffix)
    saveAsImage(data, 'slices/' + filename + suffix)

def generateCuts(data, min, numLayers):
    layerHeight = (data.max() - min) / numLayers

    for i in range(1, numLayers+1):
        upper = (data.max() - (layerHeight * (i-1)))
        lower = (data.max() - (layerHeight * i))
        
        makeSlice(data, lower, upper)




saveAsImage(clipLowerBound(cleanedData, 'heightmaps/' + filename)

#generateCuts(cleanedData, -25, 50)


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

