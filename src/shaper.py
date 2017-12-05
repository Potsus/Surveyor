import cairocffi as cairo 
from helpers import *
from scipy.interpolate import splprep, splev
import numpy as np
import sys
import math
import skimage.morphology as labeler
from shape import Shape

#takes a black and white image and converts it to smoothe vector shapes
#does not do edge detection
#does not draw the shapes
#only returns lists of tuples ordered to be drawn


#TODO: actually figure out what the water level is

class Shaper:

    def __init__(self, data):
        self.data = data

        self.shapes = []
        self.vectors = []
        self.groups = dict()
        self.centers = []

        self.groupPoints()
        self.createShapes()
        #self.sortShapes()

    def getConnections(self):
        lines = []
        for shape in self.shapes:
            lines.extend(shape.getConnects())
        return lines

    def groupPoints(self):
        data = labeler.label(self.data)

        for i in range(len(data)):
            for j in range(len(data[i])):
                point = data[i][j]
                if(point != 0):
                    if(point in self.groups):
                        self.groups[point].append((i,j))
                    else:
                        self.groups[point] = list()
                        self.groups[point].append((i,j))
        

    def createShapes(self):
        for key, group in self.groups.iteritems():
            self.shapes.append(Shape(group))


    def sortShapes(self):
        for shape in self.shapes:
            shape.sortPoints()
            

    def closePoint(self, curPoint):
        buds = self.closeBuds(curPoint)
        for bud in buds:
            i = locInList(bud, self.points)
            if i != False:
                self.shapes.append([curPoint, self.points.pop(i)])
                return True

        return False

    def closeBuds(self, curPoint):
        x,y = curPoint
        #remember that the axes are reversed
        return self.edger.orderedBuds(x,y)

    def closeShape(self, curPoint):
        buds = self.closeBuds(curPoint)
        for i in range(0, len(self.shapes)):
            for bud in buds:
                if bud == self.shapes[i][0]:
                    self.shapes[i].insert(0, curPoint)
                    return True
                elif bud == self.shapes[i][-1]:
                    self.shapes[i].append(curPoint)
                    return True

        return False


    def midShape(self, curPoint):
        #TODO: MAKE THIS WORK BETTER, currently leaves may points detached
        buds = self.closeBuds(curPoint)
        for bud in buds:
            for i in range(0, len(self.shapes)):
                j = locInList(bud, self.shapes[i])
                if j != False:
                    print('found a potential insertion point at %s' % j)
                    for sud in buds:
                        k = locInList(sud, self.shapes[i])
                        if k != False:
                            print('found best place at %s and %s' % (k, j))
                            if k < j:
                                print('inserting to the right')
                                self.shapes[i].insert(j, curPoint)
                                print('inserted to the right')
                                return True
                            if k > j:
                                print('inserting to the left')
                                self.shapes[i].insert(k, curPoint)
                                print('inserted to the left')
                                return True
                    print('inserting to the center')
                    #self.shapes[i].insert(j, self.shapes[i][j])
                    self.shapes[i].insert(j, curPoint)
                    print('inserted to the center')
                    return True

    def fixEnds(self):
        for i in range(0, len(self.shapes)):
            for j in range(1, len(self.shapes[i])-1):
                if self.shapes[i][j][0] == self.shapes[i][j-1][0] and self.shapes[i][j][0] == self.shapes[i][j+1][0]:
                    self.rotateShapeTo(i,j)
                    return True


    def rotateShapeTo(self, shapeIndex, i):
        print('rotating shape end to %s' % i)
        fragment1 = self.shapes[shapeIndex][:i-1] 
        fragment2 = self.shapes[shapeIndex][i-1:]
        self.shapes[shapeIndex] = fragment2 + fragment1   

    def padEnds(self):
        for i in range(0, len(self.shapes)):
            self.shapes[i].append(self.shapes[i][0])    
            self.shapes[i].append(self.shapes[i][1]) 

    def clipEnds(self):
        for i in range(0, len(self.shapes)):
            self.shapes[i].pop()
            self.shapes[i].pop()

    def smoothShape(self, shape, s=5, k=2, f=4):
        print('creating smooth shape # of length %s' % len(shape))
        # Smoothing the shape.
        # spline parameters
        #s = 5.0 # smoothness parameter
        #k = 2 # spline order
        #nest = -1 # estimate of number of knots needed (-1 = maximal)
        #f = 4 #how many samples you want to reduce by


        print('unzipping shape')
        x,y = zip(*shape)
        if len(x) < 10:
            return zip(x,y)
        print('splprep')
        t, u = splprep([x, y], s=s, k=k, nest=-1)
        print('splprep finished')

        samples = int(len(x)/f)
        if samples > len(shape) or samples == 0:
            samples = len(shape)*2

        print('taking %s samples' % samples)

        xn, yn = splev(np.linspace(0, 1, samples), t)  
        print('splev finished')
        return zip(xn, yn)     

    def cleanupShapes(self):
        print('joining shapes')
        while not self.joinShapes():
            #print("%s self.shapes, %s points total" % (len(self.shapes), self.numPoints()))
            pass

        while self.shapesOnly():
            pass
        self.fixEnds()
        self.padEnds()
        for i in range(0, len(self.shapes)):
            self.shapes[i] = self.smoothShape(self.shapes[i], 80)
            #self.shapes[i].reverse()
        self.clipEnds()

        while self.shapes:
            self.drawables.append(self.shapes.pop())
            pass


    def shapesOnly(self):
        print('removing points and line segments')
        for i in range(0, len(self.shapes)):
            if type(self.shapes[i]) == tuple:
                self.drawables.append(self.shapes[i].pop())
                return True
            if len(self.shapes[i]) == 2:
                self.drawables.append(self.shapes[i].pop())
                return True
        return False

    def createRing(self, depth):
        self.getPointsAtDepth(depth)
        #print('ordering %s points' % len(self.points))
        self.orderPoints()
        #print('cleaning up %s shapes' % len(self.shapes))
        self.cleanupShapes()
        #print('clearing shapes and points')
        #self.shapes = []
        #self.points = []
        #print('there are %s shapes and %s points left' % (len(self.shapes), len(self.points)))
        print ''

    def createRings(self, minimum, layerHeight):
        numLayers = int((self.data.max() - minimum)/layerHeight)
        for i in range(0, numLayers):
            #print('getting points at depth %s' % (minimum+(layerHeight * i)))
            self.createRing(minimum + (layerHeight * i))


