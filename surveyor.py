
from datetime import datetime
import requests
from io import BytesIO
import json
import numpy as np
import os.path
import gc

from helpers import *

from calculate import TICK as baseTick

from location import Location

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
        self.eGrid = []
        self.rezedGrid = []

        self.quality = 64
        self.tick = baseTick
        self.currentLine = 0
        self.setup()
        self.updateProps()


    def setup(self):
        self.rootdir     = 'Locations/%s/' % self.name
        self.rawdir      = self.rootdir + 'raw/'
        self.maptilesdir = self.rootdir + 'maptiles/'
        self.slicesdir   = self.rootdir + 'slices/'
        self.vectorsdir  = self.rootdir + 'vectors/'
        self.heightsdir  = self.rootdir + 'heightmaps/'
        self.rezdir      = self.rootdir + 'resolutions/'

        ensure_dir(self.rootdir)
        ensure_dir(self.rawdir)
        ensure_dir(self.maptilesdir)
        ensure_dir(self.slicesdir)
        ensure_dir(self.vectorsdir)
        ensure_dir(self.heightsdir)
        ensure_dir(self.rezdir)


        self.loc = Location(self.name , self.north , self.south , self.east , self.west)

        self.loc.toYaml(self.rootdir + 'config')

    def scan(self):
        if self.eGrid != []:
            self.resumeScan()
            return False
        elif config['useCache'] and self.loadHeights():
            self.loadRez()
            self.resumeScan()
            return True
        else:
            self.getGrid()

    def getGrid(self):
        choice = raw_input('fetching grid sized %s x %s from row %s is this ok? (y/n) ' % (self.xResolution, self.yResolution, self.currentLine))
        if choice != 'y':
            #quit if we don't want to continue
            return False

        #get data from google
        for y in range (self.currentLine, self.yResolution):

            sampleLat = self.north - (self.tick * y)
            print 'fetching gridline %s of %s' % (str(y), self.yResolution)
            row = self.getRow(sampleLat)
            self.eGrid.append(cleanRow(row))
            #self.rezedGrid.append(rezRow(row))
            #print(' complete')
        self.save()


    def getRow(self, lat):
        x   = 0
        row = []
        while(x < self.xResolution):
            #make sure you don't go past elevation resolution
            samplesToRequest = config['max_samples_per_request']
            if(x + samplesToRequest > self.xResolution):
                samplesToRequest = self.xResolution - x

            row.extend(self.requestLineFragment(lat, samplesToRequest, x))
            #print x,
            x += samplesToRequest
        return row

    def resumeScan(self):
        if self.checkCompleteness() == False:
                self.clipJunk()
                self.getGrid()
    
    def requestLineFragment(self, lineLat, samples, start):
        #if we've run out of keys return junk data
        if (self.keyNum >= len(config['keys'])):
            return makeJunkData(samples)

        lineLng = self.east - (self.tick * start)

        queryString  = "%s?path=%s,%s|%s,%s&samples=%s&key=%s" % (config['urls']['elevation'], lineLat, lineLng, lineLat, lineLng - (self.tick * (samples -1)), samples, config['keys'][self.keyNum])
        response     = requests.get(queryString)
        
        try:
            responseData = json.loads(response.content)
        except(e):
            print(e.message + " filling with junk")
            return makeJunkData(samples)

        if responseData['status'] != 'OK':
            print('response error: %s' % responseData['status'])
            self.useNextKey()
            return self.requestLineFragment(lineLat, samples, start)

        return responseData['results']

    def checkCompleteness(self):
        for i, row in enumerate(self.eGrid):
            if checkRow(row):
                self.currentLine = i
                print('scan incomplete on row: %s' % i)
                return False
        print('scan is complete')
        return True

    def clipJunk(self):
        del self.eGrid[self.currentLine:]
        del self.rezedGrid[self.currentLine:]


    def save(self):
        if self.eGrid != []:
            writeCsv(self.eGrid, self.rawdir + self.filename)
        if self.rezedGrid != []:
            writeCsv(self.rezedGrid, self.rezdir + self.filename)

    def setQuality(self, quality):
        self.save()
        self.clearData()
        self.quality = quality
        self.updateProps()

    def updateProps(self):
        self.tick = baseTick * self.quality

        self.xResolution = self.ticksToResolution(self.east, self.west)
        self.yResolution = self.ticksToResolution(self.north, self.south)

        self.filename = '%sx%s' % (self.xResolution, self.yResolution)

    def clearData(self):
        self.eGrid = []
        gc.collect()


    def loadHeights(self):
        rawfile = self.rawdir + self.filename
        if os.path.isfile(rawfile + '.csv') & config['useCache'] == 1:
            print('loading data from ' + rawfile + '.csv')
            self.eGrid = loadCsv(rawfile)
            self.eGrid = gridToFloats(self.eGrid)
            return True
        return False

    def loadRez(self):
        rezfile = self.rezdir + self.filename
        if os.path.isfile(rezfile + '.csv') & config['useCache'] == 1:
            print('loading data from ' + rezfile + '.csv')
            self.rezedGrid = loadCsv(rezfile)
            self.rezedGrid = gridToFloats(self.rezedGrid)
            return True
        return False

    def loadFromFile(rawfile):
        if os.path.isfile(rawfile):
            print('loading data from ' + rawfile)
            self.eGrid = importOrderedJson(rawfile)
            self.xResolution = len(self.eGrid)
            self.yResolution = len(self.eGrid[0])
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

    def saveHeightmap(self, filename):
        if self.eGrid != []:
            saveAsImage(self.eGrid, self.rootdir + filename)

    def saveRezGrid(self):
        if self.rezedGrid != []:
            saveAsImage(self.rezedGrid, self.rootdir + 'rezolution map')

    def generatePreviews(self):
        self.saveHeightmap('preview')
        #self.saveRezGrid()


    def cleanSlice(self, data, lower, upper, prefix):
        data = np.clip(data, lower, upper)
        suffix = ('%s-%s' % (lower, upper))
        print('generating image with bounds %s' % suffix)
        saveAsImage(data, self.slicesdir + '%s %s %s' % (prefix, self.filename, suffix))

    def generateCleanCuts(self, minimum, layerHeight):
        numLayers = int((self.eGrid.max() - minimum)/layerHeight)
        empty_dir(self.slicesdir)
        for i in range(0, numLayers):
            upper = (minimum + (layerHeight * (i+1)))
            lower = (minimum + (layerHeight * i))
            self.cleanSlice(self.eGrid, lower, upper, str(i).zfill(4))
            i = i+1


    def listScans(self):
        return getVisibleFiles(self.rawdir)

junkDatum = -1
junkSample = json.loads('{"elevation": %s, "location": {"lat": 0, "lng": 0}, "resolution": %s}' % (junkDatum, junkDatum))

def makeJunkData(samples):
    junkData = []
    for i in range(0, samples):
        junkData.append(junkSample)
    return junkData


def getFragmentSamples(desiredSamples):
    if desiredSamples > config['max_samples_per_request']:
        return getFragmentSamples(desiredSamples/2)
    return int(math.floor(desiredSamples))

def getElevation(location):
    return location['elevation']

def cleanRow(row):
    cleanedRow = map(getElevation, row)
    return cleanedRow

def cleanGrid(grid):
    eGrid = map(cleanRow, grid)
    return eGrid

def rezGrid(grid):
    rGrid = map(rezRow, grid)
    return rGrid

def getRez(location):
    return location['resolution']

def rezRow(row):
    rezRow = map(getRez, row)
    return rezRow

def checkRow(row):
    #TODO: could potentially leave a half finished row
    return row[0] == junkDatum

