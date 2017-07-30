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
config = importYaml('config')

#goompy stuff
#from Tkinter import Tk, Canvas, Label, Frame, IntVar, Radiobutton, Button
#from PIL import ImageTk
#from goompy import GooMPy

#create google maps interface
gmaps = googlemaps.Client(key=config['keys'][0])



#styles = importYaml('styles')

locations = importYaml('locations')


#present location options
locChoice = raw_input('pick a location to scan ' + str(locations.keys()) + ' :')
#locChoice = 'vi'


#load selection data
if keyExists(locations, locChoice):
    location = locations[locChoice]
else:
    print("not a listed location, geocoding...")
    geocode_result = gmaps.geocode(locChoice)
    print('found : ' + geocode_result[0]['address_components'][0]['long_name'])
    #check if the location is already in the list but just mistyped
    if nameLookup(geocode_result[0]['address_components'][0]['long_name'], locations) == False:
        print('not listed under a different name, adding to locations list...')
        #create a location
        location = {}
        location['name'] = geocode_result[0]['address_components'][0]['long_name']
        location['bounds'] = {}
        location['bounds']['north'] = geocode_result[0]['geometry']['viewport']['northeast']['lat']
        location['bounds']['south'] = geocode_result[0]['geometry']['viewport']['southwest']['lat']
        location['bounds']['east']  = geocode_result[0]['geometry']['viewport']['northeast']['lng']
        location['bounds']['west']  = geocode_result[0]['geometry']['viewport']['southwest']['lng']

        locations[locChoice] = location

        saveYaml(locations, 'locations')
    else:
        location = nameLookup(geocode_result[0]['address_components'][0]['long_name'], locations)

#location is now defined

# approximate the quality we want
# 1 is ~600 dpi for our wall size, but we need to improve calculate before it's really going to have any meaning
# 2 = 300 dpi, 4 = 150 dpi, 8 = 75 dpi and so forth
# we can probably get away with approximating from a lesser quality 
#parts of the map have different resolutions and may require fewer samples to get all relevant data

quality = raw_input('How fine do you want the sampling? (0: 600 dpi - 8: 75 dpi etc.)')
if canCastToInt(quality) == False:
    print("couldn't get a number there, defaulting to 64")
    quality = 64
else: quality = int(quality)
#quality = 64


#import logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
print('starting surveyor')
print('target is: ' + location['name'])

mapper = surveyor(location['name'], location['bounds']['north'], location['bounds']['south'], location['bounds']['east'], location['bounds']['west'])
mapper.setQuality(quality)
mapper.scan()
mapper.extractHeights()
saveAsImage(clipLowerBound(mapper.cleanedGrid, mapper.cleanedGrid.min()), 'heightmaps/' + mapper.filename)
mapper.generateCleanCuts(int(mapper.cleanedGrid.min()), 5)

#cleanedData = np.array(cleanGrid(mapper.getRawData()))
#generateCuts(cleanedData, -25, 50)

#showImage(clipLowerBound(cleanedData, -20))

#print('cleaning data...')
#cleanedData = np.array(cleanGrid(elevationGrid))
#np.save('%s cleaned' % filename, cleanedData)


#clipLowerBound(cleanedData, -25)

#writeJsonToFile(cleanedData, filename + ' cleaned.json')


#saveAsImage(clipLowerBound(cleanedData, 'heightmaps/' + filename, -20))

#generateCuts(cleanedData, -25, 50)




#queryString = staticMapUrl+'?'+objectToString(options, '=', '&')+'&'+stylesToString(styles)+'&key='+config['keys'][keyNum]

#first shot at a hardcoded url
#response = requests.get('https://maps.googleapis.com/maps/api/staticmap?center=mosquito+island&maptype=terrain&scale=2&size=320x320&style=feature:all|element:labels|visibility:off&style=feature:water|element:geometry.stroke|color:0x000000&key=AIzaSyAu4ptX5HdhsJvuK3gDaSwgIk7PpFRoAUg')

#response = requests.get(queryString)
#picture = Image.open(BytesIO(response.content))

#out = picture.crop((0, 0, 640, 595))

#out.save('out.png')

