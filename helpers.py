import json
import math
import numpy as np 
import yaml
import os
from PIL import Image, ImageOps, ImageDraw
import PIL.ImageOps
import ujson
import hashlib

def superJsonImport(filename):
    with open( (filename + '.json') ) as json_data:
        return ujson.load(json_data)

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

def fileExists(filename):
    return os.path.isfile(filename)


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

def convertToArray(data):
    if type(data) == list:
        imageData = np.array(data)
    elif type(data) == np.ndarray:
        imageData = data
    else:
        try:
            imageData = np.array(data)
        except(e):
            print("that didn't work")
            print(e.message())
    return imageData

def convertToImage(data):
    imageData = convertToArray(data)
    
    imageData = compressRange(imageData)
    imageData = Image.fromarray(imageData.astype('uint8'))
    imageData = PIL.ImageOps.invert(imageData)
    #imageData = imageData.transpose(Image.FLIP_LEFT_RIGHT)
    return imageData

def locInList(needle, haystack):
        try:
            i = haystack.index(needle)
            return i
        except ValueError:
            return False

def yn():
    ans = raw_input("y/n? ")
    if ans.lower() == 'y':
        return True
    return False

def writeCsv(data, filename):
    import csv
    with open(filename + ".csv", "wb") as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerows(data)

def loadCsv(filename):
    import csv
    data = []
    with open(filename + '.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, dialect='excel')
        for row in reader:
            data.append(row)
        return data

def gridToFloats(grid):
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                grid[i][j] = float(grid[i][j])
        return grid

def getLocation(locChoice=None):
    locations = importYaml('locations')

    if locChoice == None:
        print 'pick a location to scan:'
        locChoice = raw_input(str(locations.keys()) + ': ')


    if keyExists(locations, locChoice):
        location = locations[locChoice]
    else:
        print("not a listed location, geocoding...")
        geocode_result = gmaps.geocode(locChoice)
        print('found : ' + geocode_result[0]['address_components'][0]['long_name'])
        #check if the location is already in the list but just mistyped
        if nameLookup(geocode_result[0]['address_components'][0]['long_name'], locations) == False:
            print('not listed under a different name, adding to locations list...')
            #create a location
            location = {}
            location['name'] = geocode_result[0]['address_components'][0]['long_name']
            location['bounds'] = {}
            location['bounds']['north'] = geocode_result[0]['geometry']['viewport']['northeast']['lat']
            location['bounds']['south'] = geocode_result[0]['geometry']['viewport']['southwest']['lat']
            location['bounds']['east']  = geocode_result[0]['geometry']['viewport']['northeast']['lng']
            location['bounds']['west']  = geocode_result[0]['geometry']['viewport']['southwest']['lng']

            locations[locChoice] = location

            saveYaml(locations, 'locations')
        else:
            location = nameLookup(geocode_result[0]['address_components'][0]['long_name'], locations)
    return location

def getValue(message, testfunc):
    value = raw_input(str(message)+' ')
    if testfunc(value):
        return value
    else:
        getValue(message, testfunc)

def arrayAlter(data, needle, alterfunc):
    for i in range(len(data)):
        for j in range(len(data[i])):
            if data[i][j] == needle:
                data[i][j] = alterfunc(data[i][j])

def nullToGarbage(val):
    return -1

def hash(var):
    return hashlib.md5(var).hexdigest()

def hashCompare(a,b):
    return hash(a) == hash(b)

def arrayFlipLR(data):
    for i in range(0,len(data)):
        data[i] = list(reversed(data[i]))
    return data

def drawCross(pic):
    width, height = pic.size
    #print('image mode: %s' % pic.mode)
    #red = (255, 0, 0)
    pic = pic.convert('RGBA')

    # get a drawing context
    d = ImageDraw.Draw(pic)

    # draw red lines over image
    d.line( [(width/2,0),(width/2, height)], fill=(255, 0, 0, 128), width = 1)
    d.line( [(0,height/2),(width, height/2)], fill=(255, 0, 0, 128), width = 1)
    d.line((0, 0) + pic.size, fill=(255, 0, 0, 128), width = 1)
    d.line((0, pic.size[1], pic.size[0], 0), fill=(255, 0, 0, 128), width = 1)

    return pic



def pilToCairo(data):
    nptile = data.convert('RBGA')
    h,w,c = nptile.shape
    ctile = cairo.ImageSurface.create_for_data(nptile, cairo.FORMAT_RGB24, w,h)

def pil2cairo(im):
    """Transform a PIL Image into a Cairo ImageSurface."""

    assert sys.byteorder == 'little', 'We don\'t support big endian'
    if im.mode != 'RGBA':
        im = im.convert('RGBA')

    s = im.tobytes('raw', 'BGRA')
    a = array.array('B', s)
    dest = cairo.ImageSurface(cairo.FORMAT_ARGB32, im.size[0], im.size[1])
    ctx = cairo.Context(dest)
    non_premult_src_wo_alpha = cairo.ImageSurface.create_for_data(
        a, cairo.FORMAT_RGB24, im.size[0], im.size[1])
    non_premult_src_alpha = cairo.ImageSurface.create_for_data(
        a, cairo.FORMAT_ARGB32, im.size[0], im.size[1])
    ctx.set_source_surface(non_premult_src_wo_alpha)
    ctx.mask_surface(non_premult_src_alpha)
    return dest

