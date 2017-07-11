import googlemaps
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO
import json

#goompy stuff
#from Tkinter import Tk, Canvas, Label, Frame, IntVar, Radiobutton, Button
#from PIL import ImageTk
#from goompy import GooMPy

#my stuff
from helpers import *
from keys import gmapsApiKey

gmaps = googlemaps.Client(key=gmapsApiKey)
options = importJson('options.json')

#move the styles into a seperate list
styles = options.pop('styles')

# Geocoding an address
#geocode_result = gmaps.geocode(options.pop('center'))


staticMapUrl = "https://maps.googleapis.com/maps/api/staticmap"


queryString = staticMapUrl+'?'+objectToString(options, '=', '&')+'&'+urlStyles(styles)+'&key='+gmapsApiKey

#first shot at a hardcoded url
#response = requests.get('https://maps.googleapis.com/maps/api/staticmap?center=mosquito+island&maptype=terrain&scale=2&size=320x320&style=feature:all|element:labels|visibility:off&style=feature:water|element:geometry.stroke|color:0x000000&key=AIzaSyAu4ptX5HdhsJvuK3gDaSwgIk7PpFRoAUg')

response = requests.get(queryString)
picture = Image.open(BytesIO(response.content))

out = picture.crop((0, 0, 640, 595))

out.save('out.png')

