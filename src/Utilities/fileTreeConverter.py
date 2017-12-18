#convert old file structure to new surveyor class file structure

import googlemaps
from io import BytesIO
import os.path
from lazyme.string import color_print

from helpers import *
from surveyor import *
config = importYaml('config')

#create google maps interface
gmaps = googlemaps.Client(key=config['keys'][0])

locations = importYaml('locations')


#get the dimensions of the images we're working with
path = 'heightmaps/'
files = getVisibleFiles(path)
print('found:')
print(files)

for filename in files:
    #get each file and location data
    loc, newName = filename.split(' at ')
    #loc = filename
    color_print('working on ' + loc, color='yellow', bold=True)
    location = nameLookup(loc, locations)
    print('found config ')
    print(location)

    #print('creating file structure')
    mapper = surveyor(location['name'], location['bounds']['north'], location['bounds']['south'], location['bounds']['east'], location['bounds']['west'])
    oldName = (path + filename)
    newName = (mapper.rootdir + "preview.png")
    print('moving %s to %s' % (oldName, newName))
    os.rename(oldName, newName)
    #mapper.loadFromFile(filename)


    color_print('done', color='green')
    print('')
    print('')