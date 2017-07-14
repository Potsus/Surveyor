import json
import math
import numpy as np 

def importJson(file):
    from collections import OrderedDict
    with open(file) as json_data:
        return json.load(json_data, object_pairs_hook=OrderedDict)

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
    with open(str(filename), 'w') as outfile:
        json.dump(variable, outfile, ensure_ascii=False)


def getElevation(location):
    return location['elevation']

def cleanRow(row):
    cleanedRow = map(getElevation, row)
    return cleanedRow

def cleanGrid(grid):
    cleanedGrid = map(cleanRow, grid)
    return cleanedGrid

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
