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
from keys import gmapsApiKey

gmaps = googlemaps.Client(key=gmapsApiKey)
options = importJson('options.json')
MAP_RESOLUTION = 320
SCALE = 2
ELEVATION_RESOLUTION = (MAP_RESOLUTION * SCALE)/1

staticMapUrl = "https://maps.googleapis.com/maps/api/staticmap"
elevationUrl = 'https://maps.googleapis.com/maps/api/elevation/json'

#move the styles into a seperate list
styles = options.pop('styles')

# Geocoding an address
geocode_result = gmaps.geocode('mosquito island')

lat = geocode_result[0]['geometry']['location']['lat']
lng = geocode_result[0]['geometry']['location']['lng']

#bounds   = geocode_result[0]['geometry']['bounds']
viewport = geocode_result[0]['geometry']['viewport']
#viewport['northeast']['lat'] = 18.532035
#viewport['northeast']['lng'] = -64.324514
#viewport['southwest']['lat'] = 18.271421
#viewport['southwest']['lng'] = -65.105230


latDiff = ((viewport['northeast']['lat'] - viewport['southwest']['lat'])/ELEVATION_RESOLUTION)
lngDiff = ((viewport['northeast']['lng'] - viewport['southwest']['lng'])/ELEVATION_RESOLUTION)

elevationGrid = []


#for y in range (0, ELEVATION_RESOLUTION):
#	#latitude to sample from should be derived from viewport bounds and the elevation resolution
#	sampleLat = viewport['southwest']['lat'] + (latDiff * y)
#	for x in range (0, ELEVATION_RESOLUTION):
#		sampleLng = viewport['northeast']['lng'] + (lngDiff * x)
filename = '%s, %s at %s' % (lat, lng, ELEVATION_RESOLUTION)

if os.path.isfile('raw/' + filename + '.json'):
	elevationGrid = importJson('raw/' + filename + '.json')
else:
	for y in range (0, ELEVATION_RESOLUTION):
		sampleLat    = viewport['northeast']['lat'] - (latDiff * y)
		queryString  = "%s?path=%s,%s|%s,%s&samples=%s&key=%s" % (elevationUrl, sampleLat, viewport['northeast']['lng'], sampleLat, viewport['southwest']['lng'], ELEVATION_RESOLUTION, gmapsApiKey)
		response     = requests.get(queryString)
		responseData = json.loads(response.content)
		elevationGrid.append(responseData['results'])
		logging.debug('completed gridline %s' % y)
		#sleep(0.25)

	writeJsonToFile(elevationGrid, 'raw/' + filename + '.json')


cleanedData = np.array(cleanGrid(elevationGrid))
#cleanedData[cleanedData < 0] = 0
#writeJsonToFile(cleanedData, filename + ' cleaned.json')

imageData = (255*(cleanedData - np.max(cleanedData))/-np.ptp(cleanedData)).astype(int)

#generate heightmap
heightMap = Image.fromarray(imageData.astype('uint8'))
heightMap = PIL.ImageOps.invert(heightMap)
heightMap = heightMap.transpose(Image.FLIP_LEFT_RIGHT)
heightMap.save('heightmaps/' + filename + '.png')

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



queryString = staticMapUrl+'?'+objectToString(options, '=', '&')+'&'+stylesToString(styles)+'&key='+gmapsApiKey

#first shot at a hardcoded url
#response = requests.get('https://maps.googleapis.com/maps/api/staticmap?center=mosquito+island&maptype=terrain&scale=2&size=320x320&style=feature:all|element:labels|visibility:off&style=feature:water|element:geometry.stroke|color:0x000000&key=AIzaSyAu4ptX5HdhsJvuK3gDaSwgIk7PpFRoAUg')

#response = requests.get(queryString)
#picture = Image.open(BytesIO(response.content))

#out = picture.crop((0, 0, 640, 595))

#out.save('out.png')

