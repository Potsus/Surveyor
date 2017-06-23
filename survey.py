import googlemaps
from datetime import datetime
from keys import gmapsApiKey

gmaps = googlemaps.Client(key=gmapsApiKey)

# Geocoding an address
geocode_result = gmaps.geocode('British Virgin Islands')