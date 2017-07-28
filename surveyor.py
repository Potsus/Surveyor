
from datetime import datetime
import requests
from PIL import Image
import PIL.ImageOps
from io import BytesIO
import json
import numpy as np
import os.path
import yaml
import gc

from helpers import *

from calculate import TICK as baseTick

junkSample = json.loads('{"elevation": 0, "location": {"lat": 0, "lng": 0}, "resolution": 0}')
config = importYaml('config')



class surveyor:
    #shared data
    keyNum = 0

    def __init__(self, name, north, south, east, west):
        #data specific to an instance of surveyor
        self.name  = name
        self.north = north
        self.south = south
        self.east  = east
        self.west  = west
        self.elevationGrid = []

        self.quality = 64
        self.updateProps()


    def scan(self):
        if self.elevationGrid != []:
            return False
        elif self.loadArea():
            return True
        else:
            choice = raw_input('fetching grid sized %s x %s is this ok? (y/n) ' % (self.xResolution, self.yResolution))
            if choice != 'y':
                #quit if we don't want to continue
                exit()

            #get data from google
            for y in range (0, yResolution):

                sampleLat = north - (TICK * y)
                
                self.elevationGrid.append(getRow(sampleLat))
                print('completed gridline %s of %s' % (y, yResolution))

            self.saveCollectedData()


    def getData(self):
        return self.elevationGrid

    def saveCollectedData(self):
        if self.elevationGrid != []:
            writeJsonToFile(self.elevationGrid, 'raw/' + self.filename)

    def setQuality(self, quality):
        self.saveCollectedData()
        self.clearData()
        self.quality = quality
        self.updateProps()

    def updateProps(self):
        self.tick = baseTick * self.quality

        self.xResolution = self.ticksToResolution(self.east, self.west)
        self.yResolution = self.ticksToResolution(self.north, self.south)

        self.filename = '%s at %sx%s' % (self.name, self.xResolution, self.yResolution)

    def clearData(self):
        self.elevationGrid = []
        self.cleanedData = None
        gc.collect()


    def loadArea(self):
        #if i already have data load it
        if os.path.isfile('raw/' + self.filename + '.json') & config['useCache'] == 1:
            print('loading data from raw/' + self.filename + '.json')
            self.elevationGrid = importOrderedJson('raw/' + self.filename)
            return True
        return False

    def ticksToResolution(self, a,b):
        #no longer needed because resolution doesn't have to devide into even numbers
        #pixels should be sampled in the center of their pixel
        #this will almost never devide evenly for the last line segment in a row
        #but the deviance is practically nothing for most purposes
        #return roundToEven(abs(a - b) / TICK)
        return int(math.ceil(abs(a - b) / (baseTick * self.quality)))

    def useNextKey(self):
        self.keyNum += 1





def makeJunkData(samples):
    junkData = []
    for i in range(0, samples):
        junkData.append(junkSample)
    return junkData

def getFragmentSamples(desiredSamples):
    if desiredSamples > config['max_samples_per_request']:
        return getFragmentSamples(desiredSamples/2)
    return int(math.floor(desiredSamples))

def requestLineFragment(lineLat, samples, start):
    #if we've run out of keys return junk data
    if (keyNum >= len(config['keys'])):
        return makeJunkData(samples)

    lineLng = location['bounds']['east'] - (TICK * start)

    queryString  = "%s?path=%s,%s|%s,%s&samples=%s&key=%s" % (config['urls']['elevation'], lineLat, lineLng, lineLat, lineLng - (TICK * (samples -1)), samples, config['keys'][keyNum])
    response     = requests.get(queryString)
    responseData = json.loads(response.content)
    if responseData['status'] != 'OK':
        logging.debug('response error: %s' % responseData['status'])
        useNextKey()
        return requestLineFragment(lineLat, samples, start)

    return responseData['results']



def getLat(point):
    return point['location']['lng']

def getRow(lat):
    x   = 0
    row = []
    while(x < xResolution):
        #make sure you don't go past elevation resolution
        if(x + samplesToRequest > xResolution):
            samplesToRequest = xResolution - x
        else:
            samplesToRequest = config['max_samples_per_request']

        row.extend(requestLineFragment(lat, samplesToRequest, x))
        print x,
        x += samplesToRequest
    return row

def clipLowerBound(dataArray, lowerBound):
    return np.clip(dataArray, lowerBound, dataArray.max())

def compressRange(data):
    return (255*(data - np.max(data))/-np.ptp(data)).astype(int)

def convertToImage(data):
    imageData = compressRange(data)
    imageData = Image.fromarray(imageData.astype('uint8'))
    imageData = PIL.ImageOps.invert(imageData)
    imageData = imageData.transpose(Image.FLIP_LEFT_RIGHT)
    return imageData


def saveAsImage(data, filename):
    imageData = convertToImage(data)
    imageData.save(filename + '.png')

def makeSlice(data, lower, upper):
    data = np.clip(data, lower, upper)
    suffix = (' %s-%s' % (upper, lower))
    print('generating image with bounds %s' % suffix)
    saveAsImage(data, 'slices/' + filename + suffix)

def generateCuts(data, min, numLayers):
    layerHeight = (data.max() - min) / numLayers

    for i in range(1, numLayers+1):
        upper = (data.max() - (layerHeight * (i-1)))
        lower = (data.max() - (layerHeight * i))
        
        makeSlice(data, lower, upper)

def showImage(data):
    image = convertToImage(data)
    image.show()


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

