import json
import math
import numpy as np 
import yaml

def importOrderedJson(filename):
    from collections import OrderedDict
    with open( (filename + '.json') ) as json_data:
        return json.load(json_data, object_pairs_hook=OrderedDict)

#loads a json file with specified handle
def importJson(filename):
    with open( (filename + '.json') ) as json_data:
        return json.load(json_data)

#loads a yaml file with specified handle
def importYaml(filename):
    with open( (filename + '.yaml') ) as yaml_data:
        return yaml.safe_load(yaml_data)

def saveYaml(yaml_data, filename):
    with file( (filename + '.yaml'), 'w+') as yaml_file:
        yaml.safe_dump(yaml_data, yaml_file, default_flow_style=False)

def stylesToString(styles):
    stringifiedStyles = list(map(styleString, styles))
    string = '&'.join(stringifiedStyles)
    return string


def styleString(element):
    string = 'style=' + objectToString(element, ':', '|') 
    return string
        

def objectToString(object, pairSeperator, objectSeperator):
    #TODO clean this up, break it out into seperate lines
    return str(objectSeperator).join(['%s%s%s' % (key,pairSeperator, value) for (key, value) in object.items()])

def writeJsonToFile(variable, filename):
    with open(str( (filename + '.json') ), 'w') as outfile:
        json.dump(variable, outfile, ensure_ascii=False)


def getElevation(location):
    return location['elevation']

def cleanRow(row):
    cleanedRow = map(getElevation, row)
    return cleanedRow

def cleanGrid(grid):
    cleanedGrid = map(cleanRow, grid)
    return cleanedGrid

def findRawRez(grid):
    rezGrid = map(rezRow, grid)
    return rezGrid

def getRez(location):
    return location['resolution']

def rezRow(row):
    rezRow = map(getRez, row)
    return rezRow

def feetToInches(feet):
    return feet * 12

def feetReadable(dist):
    feet   = math.floor(dist)
    inches = round(((dist % 1) * 12), 2)

    #format outa
    out = ''
    if feet > 0:
        out = '%sft ' % feet
    if inches > 0:
        out += ' %sin' % inches
    return out

def scaleBigToSmall(scale, dist):
    return dist/scale

def roundToEven(f):
    return int(math.ceil(f / 2.) * 2)

def listColDelete(list, col):
    for row in list:
        del row[col]

def listCol(list, col):
    for row in list:
        print row[col]


def keyExists(obj, index):
    try:
        obj[index]
    except (IndexError, KeyError):
        return False
    return True


def canCastToInt(val):
    try:
        int(val)
        return True
    except ValueError:
        return False
