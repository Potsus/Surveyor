import json
import math
import numpy as np 
import yaml
import os
from PIL import Image
import PIL.ImageOps

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

def nameLookup(name, locations):
        for location in locations.iteritems():
            if location[1]['name'] == name:
                return location[1]
        return False

def ensure_dir(directory):
    #directory = os.path.dirname(file_path)
    #print('making sure %s directory exists.' % directory)
    if not os.path.isdir(directory):
        print("%s doesn't exist. Creating..." % directory)
        try:
            os.makedirs(directory)
        except:
            print("error",sys.exc_info()[0],"occured.")

    #print("is %s a directory? %s" % (directory, os.path.isdir(directory)))


def empty_dir(directory):
    #get all non dotfiles
    files = filter( lambda f: not f.startswith('.'), os.listdir(directory))
    for f in files:
        os.remove(directory + '/' + f)

def getVisibleFiles(path):
    return filter( lambda f: not f.startswith('.'), os.listdir(path))


def saveAsImage(data, filename):
    imageData = convertToImage(data)
    imageData.save(filename + '.png')
        

def showImage(data):
    image = convertToImage(data)
    image.show()

def clipLowerBound(data, lowerBound):
    return np.clip(data, lowerBound, data.max())

def compressRange(data):
    return (255*(data - np.max(data))/-np.ptp(data)).astype(int)

def convertToImage(data):
    imageData = compressRange(data)
    imageData = Image.fromarray(imageData.astype('uint8'))
    imageData = PIL.ImageOps.invert(imageData)
    imageData = imageData.transpose(Image.FLIP_LEFT_RIGHT)
    return imageData

