import googlemaps
from datetime import datetime
from keys import gmapsApiKey
import requests
from PIL import Image
from io import BytesIO

gmaps = googlemaps.Client(key=gmapsApiKey)

staticMapUrl = "https://maps.googleapis.com/maps/api/staticmap?"

# Geocoding an address
geocode_result = gmaps.geocode('British Virgin Islands')

mapSettings = [
	{center: "mosquito island"},
	{maptype: "terrain"},
	{scale: 2},
	{size: "320x240"},
	{style: [
		{
			feature: 'road',
			elementType: 'geometry',
			style: [
				{ hue: '#000000' },
				{ saturation: -100 },
				{ lightness: -100 },
				{ visibility: 'on' }
			]
		},{
			feature: 'landscape',
			element: 'geometry',
			style: [
				{ hue: '#777777' },
				{ saturation: -100 },
				{ lightness: -48 },
				{ visibility: 'simplified' }
			]
		},{
			feature: 'transit',
			element: 'labels',
			style: [
				{ hue: '#ffffff' },
				{ saturation: 0 },
				{ lightness: 100 },
				{ visibility: 'off' }
			]
		}
	]}
]

queryString = ""





var options = {
	mapTypeControlOptions: {
		mapTypeIds: [ 'Styled']
	},
	center: new google.maps.LatLng(18.39499905671678, -64.66102679967878),
	zoom: 13,
	mapTypeId: 'Styled'
};

#first shot at a hardcoded url
#response = requests.get('https://maps.googleapis.com/maps/api/staticmap?center=mosquito+island&maptype=terrain&scale=2&size=320x320&style=feature:all|element:labels|visibility:off&style=feature:water|element:geometry.stroke|color:0x000000&key=AIzaSyAu4ptX5HdhsJvuK3gDaSwgIk7PpFRoAUg')

picture = Image.open(BytesIO(response.content))

out = picture.crop((0, 0, 640, 595))

out.save('out.png')