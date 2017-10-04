
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
        self.elevationGrid = []
        self.heightMap = np.ndarray((0,0))
        self.rezGrid = []

        self.quality = 64
        self.tick = baseTick
        self.currentLine = 0
        self.setup()
        self.updateProps()


    ######### BASIC SETUP ###########

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
        self.elevationGrid = [ [ junkDatum for x in range( self.xResolution ) ] for y in range( self.yResolution ) ]

    def clearData(self):
        self.elevationGrid = []
        gc.collect()

    def useNextKey(self):
        self.keyNum += 1

    def ticksToResolution(self, a,b):
        #no longer needed because resolution doesn't have to devide into even numbers
        #pixels should be sampled in the center of their pixel
        #this will almost never devide evenly for the last line segment in a row
        #but the deviance is practically nothing for most purposes
        #return roundToEven(abs(a - b) / TICK)
        return int(math.ceil(abs(a - b) / (baseTick * self.quality)))

    def scan(self):
        if config['useCache']:
            self.load()
            self.cleanUpScan()

        else:
            self.sampleRows(self.yResolution)


    ######## DATA RETRIEVAL #########

    def sampleRows(self, rows):
        if presentYN('Sample %s rows at %s samples per row'):
            for i, index in enumerate(rows):
                print('sampling row %s of %s.' % (i, len(rows)))
                row = self.sampleRow(lat)
                self.elevationGrid[index] = getRowElevation(row)
                #self.rezGrid.append(rezRow(row))
            self.save()


    def sampleRow(self, rowIndex):
        x   = 0
        row = []
        lat = self.north - (self.tick * rowIndex)

        while(x < self.xResolution):
            #get at most our max samples per request and not more than the difference between x and the xresolution
            samplesToRequest = min(config['max_samples_per_request'], self.xResolution - x)

            row.extend(self.sampleLineFragment(lat, samplesToRequest, x))
            #print x,
            x += samplesToRequest
        return row
    
    def sampleLineFragment(self, lineLat, samples, start):
        #if we've run out of keys return junk data
        if (self.keyNum >= len(config['keys'])):
            return makeJunkData(samples)

        lineLng = self.west + (self.tick * start)

        queryString  = "%s?path=%s,%s|%s,%s&samples=%s&key=%s" % (config['urls']['elevation'], lineLat, lineLng, lineLat, lineLng + (self.tick * (samples -1)), samples, config['keys'][self.keyNum])
        response     = requests.get(queryString)
        
        try:
            responseData = json.loads(response.content)
        except(e):
            print(e.message + " filling with junk")
            return makeJunkData(samples)

        if responseData['status'] != 'OK':
            print('response error: %s' % responseData['status'])
            self.useNextKey()
            return self.sampleLineFragment(lineLat, samples, start)

        return responseData['results']




    ########## INTEGRITY CHECK ###########

    def findIncompleteRows(self):
        incompleteRows = []
        for index, row in enumerate(self.elevationGrid):
            if rowIncomplete(row):
                incompleteRows.append(index)
        return incompleteRows


    def cleanUpScan(self):
        incompleteRows = self.findIncompleteRows()
        if incompleteRows != []:
            print('Found %s incomplete rows. ' % len(incompleteRows))
            self.sampleRows(incompleteRows)
        else:
            print('Scan has no incomplete rows')
                 


    ######### SAVING AND LOADING ##########

    def save(self):
        if self.elevationGrid != []:
            writeCsv(self.elevationGrid, self.rawdir + self.filename)
        if self.rezGrid != []:
            writeCsv(self.rezGrid, self.rezdir + self.filename)

    def load(self):
        rawfile = self.rawdir + self.filename
        self.elevationGrid = loadGridFromFile(rawfile)

        rezfile = self.rezdir + self.filename
        self.rezGrid = loadGridFromFile(rezfile)
        

    def listScans(self):
        return getVisibleFiles(self.rawdir)



    ######### CONVENIENCE FUNCTIONS #########

    def saveHeightmap(self, filename):
        if self.elevationGrid != []:
            saveAsImage(self.elevationGrid, filename)

    def saveClipped(self, minimum):
        self.makeNpArrays()
        saveAsImage(clipLowerBound(self.cleanedGrid, minimum), self.rootdir + 'preview')

    def cleanSlice(self, data, lower, upper, prefix):
        data = np.clip(data, lower, upper)
        suffix = ('%s-%s' % (lower, upper))
        print('generating image with bounds %s' % suffix)
        saveAsImage(data, self.slicesdir + '%s %s %s' % (prefix, self.filename, suffix))

    def generateCleanCuts(self, minimum, layerHeight):
        numLayers = int((self.elevationGrid.max() - minimum)/layerHeight)
        empty_dir(self.slicesdir)
        for i in range(0, numLayers):
            upper = (minimum + (layerHeight * (i+1)))
            lower = (minimum + (layerHeight * i))
            self.cleanSlice(self.elevationGrid, lower, upper, str(i).zfill(4))
            i = i+1

    def generatePreviews(self):
        self.saveHeightmap(self.rootdir + config['filetree']['elevpreview'])
        self.saveHeightmap(self.heightsdir + self.filename)
        #self.saveRezGrid()

    def saveRezGrid(self, filename):
        if self.rezGrid != []:
            saveAsImage(self.rezGrid, filename)

    def makeNpArrays(self):
        self.cleanedGrid = np.array(self.elevationGrid)
        #self.cleanRez = np.array(self.rezGrid)

    def getNpGrid(self):
        return np.array(self.elevationGrid)



#functions that do not require access to private data members


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

def getPointElevation(location):
    return location['elevation']

def getRowElevation(row):
    cleanedRow = map(getPointElevation, row)
    return cleanedRow

def getGridElevation(grid):
    elevationGrid = map(getRowElevation, grid)
    return elevationGrid

def rezGrid(grid):
    rGrid = map(rezRow, grid)
    return rGrid

def getRez(location):
    return location['resolution']

def rezRow(row):
    rezRow = map(getRez, row)
    return rezRow

def rowIncomplete(row):
    #TODO: could potentially leave a half finished row
    return row[-1] == junkDatum

def loadGridFromFile(filename):
        if os.path.isfile(filename + '.csv'):
            print('loading data from ' + filename + '.csv')
            grid = loadCsv(filename)
            grid = gridToFloats(grid)
            return grid
        return []

