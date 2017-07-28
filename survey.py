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
import yaml

from helpers import *
from surveyor import *
from calculate import TICK as softTick
config = importYaml('config.yaml')

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug('starting surveyor')

#goompy stuff
#from Tkinter import Tk, Canvas, Label, Frame, IntVar, Radiobutton, Button
#from PIL import ImageTk
#from goompy import GooMPy

# approximate the quality we want
# 1 is ~600 dpi for our wall size, but we need to improve calculate before it's really going to have any meaning
# 2 = 300 dpi, 4 = 150 dpi, 8 = 75 dpi and so forth
# we can probably get away with approximating from a lesser quality 
#parts of the map have different resolutions and may require fewer samples to get all relevant data
TICK = softTick * 32

#create google maps interface
gmaps = googlemaps.Client(key=config['keys'][0])

#keep track of which api key we're on
keyNum = 0

styles = importYaml('styles')

locations = importYaml('locations')

#present location options
locChoice = raw_input('pick a location to scan ' + str(locations.keys()) + ' :')
if keyExists(locations, locChoice):
    location = locations[locChoice]
else:
    print("not a listed location, geocoding...")
    geocode_result = gmaps.geocode(locChoice)
    print('')


location = locations['ti']





#lat = geocode_result[0]['geometry']['location']['lat']
#lng = geocode_result[0]['geometry']['location']['lng']

#bounds   = geocode_result[0]['geometry']['bounds']
#viewport = geocode_result[0]['geometry']['viewport']

#location['bounds']['north'] = viewport['location['bounds']['north']location['bounds']['east']']['lat'] 
#location['bounds']['east']  = viewport['location['bounds']['north']location['bounds']['east']']['lng']  
#location['bounds']['south'] = viewport['location['bounds']['south']location['bounds']['west']']['lat'] 
#location['bounds']['west']  = viewport['location['bounds']['south']location['bounds']['west']']['lng'] 


yResolution = ticksToResolution(location['bounds']['north'], location['bounds']['south'])
xResolution = ticksToResolution(location['bounds']['east'], location['bounds']['west'])



print('fetching grid sized %s x %s is this ok?' % (xResolution, yResolution))
sleep(4)

elevationGrid = []

junkSample = json.loads('{"elevation": 0, "location": {"lat": 0, "lng": 0}, "resolution": 0}')


filename = '%s at %sx%s' % (geocode_result[0]['address_components'][0]['short_name'], xResolution, yResolution)

#def useNextKey():
#    global keyNum
#    if (keynum < len(config['keys']))
#        keyNum += 1
#        return true
#    return false



#START THE THING

useCache = 1

#if i already have data load it
if os.path.isfile('raw/' + filename) & useCache == 1:
    logging.debug('loading data from file...')
    elevationGrid = importOrderedJson('raw/' + filename)
else:
    #


    #this is inneficent now
    #maxSamples = getFragmentSamples(xResolution)

    for y in range (0, yResolution):

        sampleLat    = location['bounds']['north'] - (TICK * y)
        
        elevationGrid.append(getRow(sampleLat))
        logging.debug('completed gridline %s of %s' % (y, yResolution))

    writeJsonToFile(elevationGrid, 'raw/' + filename)


logging.debug('cleaning data...')
cleanedData = np.array(cleanGrid(elevationGrid))
#np.save('%s cleaned' % filename, cleanedData)




saveAsImage(clipLowerBound(cleanedData, 'heightmaps/' + filename)

#generateCuts(cleanedData, -25, 50)




queryString = staticMapUrl+'?'+objectToString(options, '=', '&')+'&'+stylesToString(styles)+'&key='+config['keys'][keyNum]

#first shot at a hardcoded url
#response = requests.get('https://maps.googleapis.com/maps/api/staticmap?center=mosquito+island&maptype=terrain&scale=2&size=320x320&style=feature:all|element:labels|visibility:off&style=feature:water|element:geometry.stroke|color:0x000000&key=AIzaSyAu4ptX5HdhsJvuK3gDaSwgIk7PpFRoAUg')

#response = requests.get(queryString)
#picture = Image.open(BytesIO(response.content))

#out = picture.crop((0, 0, 640, 595))

#out.save('out.png')

