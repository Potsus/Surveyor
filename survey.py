import googlemaps
from datetime import datetime
from keys import gmapsApiKey
import requests
from PIL import Image
from io import BytesIO

gmaps = googlemaps.Client(key=gmapsApiKey)

# Geocoding an address
geocode_result = gmaps.geocode('British Virgin Islands')



response = requests.get('https://maps.googleapis.com/maps/api/staticmap?center=mosquito+island&maptype=terrain&scale=2&size=320x320&style=feature:all|element:labels|visibility:off&style=feature:water|element:geometry.stroke|color:0x000000&key=AIzaSyAu4ptX5HdhsJvuK3gDaSwgIk7PpFRoAUg')

picture = Image.open(BytesIO(response.content))

out = picture.crop((0, 0, 640, 595))

out.save('out.png')