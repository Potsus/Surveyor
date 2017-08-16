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

from calculate import TICK as tick
from helpers import *
from surveyor import *
from mapper import mapper
config = importYaml('config')
blankStyle = config['blankStyle']

gmaps = googlemaps.Client(key=config['keys'][0])


def testZoom(zoom):
    if canCastToInt(zoom) == False:
        print 'please give an int'
        return False
    mapper.setZoom(int(zoom))
    print 'is this ok?'
    return yn()

#import logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
print('starting surveyor')

mapper = mapper(location['name'], location['bounds']['north'], location['bounds']['south'], location['bounds']['east'], location['bounds']['west'])
#getValue('what zoom level would you like?', testZoom)

isoStyles = {}

def isolateFeature(feature):
    out = [blankStyle]

    for style in styles:
        if style['featureType'] == feature:
            style['hue'] = '#ffffff'
            style['visibility'] = 'on'
            out.append(style)
    return out

for  in styles:
    isoStyles[style['featureType']] = isolateFeature(style['featureType'])

mapper.set
mapper.fetchArea()

