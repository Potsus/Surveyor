from helpers import importYaml
import requests
import googlemaps

styles    = importYaml('styles')
config    = importYaml('config')
locations = importYaml('locations')

keyNum = 0

options = config['mapOptions']
staticMapUrl = config['urls']['staticMap']
blankStyle = config['blankStyle']

gmaps = googlemaps.Client(key=config['keys'][0])

isoStyles = {}

def isolateFeature(feature):
    out = [blankStyle]

    for style in styles:
        if style['featureType'] == feature:
            style['hue'] = '#ffffff'
            style['visibility'] = 'on'
            out.append(style)
    return out

for style in styles:
    isoStyles[style['featureType']] = isolateFeature(style['featureType'])

#queryString = staticMapUrl+'?'+objectToString(options, '=', '&')+'&'+stylesToString(styles)+'&key='+config['keys'][keyNum]


#for style in styles:
#    style['stylers']['lightness'] = 50
#    style['stylers']['saturation'] = 100

def objectToString(object, pairSeperator, objectSeperator):
    #TODO clean this up, break it out into seperate lines
    return str(objectSeperator).join(['%s%s%s' % (key,pairSeperator, value) for (key, value) in object.items()])

def styleString(element):
    string = 'style=' + objectToString(element, ':', '|') 
    return string

def stylesToString(styles):
    stringifiedStyles = list(map(styleString, styles))
    string = '&'.join(stringifiedStyles)
    return string

style = styles[0]

print(styleString(style))