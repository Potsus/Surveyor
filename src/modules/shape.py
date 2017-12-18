from scipy.interpolate import splprep, splev
import numpy as np
from helpers import tupleAdd
from itertools import cycle

#defines the properties of a shape and what to do with it
class Shape:
    #clockwise dict of point offsets
    coords = [
        (-1, -1),
        (0, -1),
        (1, -1),
        (1, 0),
        (1, 1),
        (0, 1),
        (-1, 1),
        (-1, 0)
    ]

    orthag = [
        (0,1),
        (1,0),
        (-1,0),
        (0,-1)
    ]

    orthagLen = len(orthag)

    coordsLen = len(coords)
    halfLen = (coordsLen/2)+1

    def __init__(self, points):
        self.points = points
        self.offset = 0
        self.dupes = []
        self.connections = []

        self.findBounds()
        self.findCenter()
        #self.sortPoints()


    def findBounds(self):
        y,x = self.points[0]
        self.left = x
        self.right = x
        self.top = y
        self.bottom = y

        for point in self.points:
            if point[1] > self.right:
                self.right = point[1]
            if point[1] < self.left:
                self.left = point[1]

            if point[0] > self.bottom:
                self.bottom = point[0]
            if point[0] < self.top:
                self.top = point[0]


    def findCenter(self):
        y = self.bottom -((self.bottom-self.top)/2)
        x = self.right -((self.right-self.left)/2)
        self.center = (y,x)

    def sortPoints(self):
        print('Sorting points in shape length %s' % len(self.points))
        self.createDupes()
        #self.trimLines()
        if len(self.points) > 0:
            self.circleSort(self.points)
            #self.orthagSort()
        

    def pointAtDirection(self, point, direction):
        return tupleAdd(point, self.coords[direction])
        
    def circleSort(self, data):
        out = []
        offset = 0
        tip = -1
        out.append(data[0]) #leave the first element in there
        for i in range(1,len(data)):

            if out[-1] == out[0] and i > 1: 
                break

            found = False

            for j in range(offset, offset+self.coordsLen): #start the loop at an offset
                needle = tupleAdd(out[tip], self.coords[j % self.coordsLen]) #always going from the tip leads to problems on single pixel penisulas
                if needle in data:
                    out.append(data.pop(data.index(needle)))
                    offset = (j+self.halfLen) % self.coordsLen
                    tip = -1 #reset the tip
                    found = True
                    break

            if found == False:
                print('miss')
                tip += -1
                i   += -1



        self.points = out

    def circleSortOrthag(self, data):
        out = []
        offset = 0
        tip = -1
        out.append(data[0]) #leave the first element in there
        for i in range(1,len(data)):

            if out[-1] == out[0] and i > 1: 
                break

            for j in range(offset, offset+self.orthagLen): #start the loop at an offset
                needle = tupleAdd(out[tip], self.orthag[j % self.orthagLen]) #always going from the tip leads to problems on single pixel penisulas
                if needle in data:
                    out.append(data.pop(data.index(needle)))
                    offset = (j+(self.orthagLen/2)) % self.orthagLen



        self.points = out

    def getOrthag(self, point):
        adj = []
        for i in range(self.offset, self.offset + self.orthagLen):
            needle = tupleAdd(point, self.orthag[i % self.orthagLen]) #always search from the left first
            if needle in self.points:
                adj.append(needle)
        return adj

    def getAdjacent(self, point):
        adj = []
        for i in range(self.offset, self.offset + self.coordsLen):
            needle = tupleAdd(point, self.coords[i % self.coordsLen]) #always search from the left first
            if needle in self.points:
                adj.append(needle)
        return adj

    def copyPoint(self, point, copies):
        for i in range(0, copies):
            self.dupes.append(point) 
        self.points.extend(self.dupes)


    def orthagSort(self):
        out = [self.points[0]]
        adj = []
        self.offset = 0
        j = 1
        finished = False

        for j in range(0, len(self.points)):
            
            adj = self.getOrthag(out[-1])

            out.append(adj[0])

            self.offset = (self.offset+(self.orthagLen/2)+1) % self.orthagLen

        self.points = out



    def createDupes(self):
        for i in range(0, len(self.points)):
            adj = self.getOrthag(self.points[i])

            extraConnects = len(adj)-2
            if  extraConnects > 0:
                self.copyPoint(self.points[i], extraConnects)


    def trimLines(self):
        i = 0
        while i < len(self.points):
            adj = self.getAdjacent(self.points[i])
            if len(adj) < 2:
                adj = self.getAdjacent(self.points[i-1])
                if len(adj) == 2:
                    self.points.pop(i)
                    i = max(i-10, 0)
                    continue
            i += 1

    def seperateDupes(self):
        pass

    def createConnects(self):
        print('creating connections in shape length %s' % len(self.points))
        for i in range(0, len(self.points)):
            adj = self.getAdjacent(self.points[i])
            for connection in adj:
                cur = [self.points[i], connection]
                if cur not in self.connections:
                    self.connections.append(cur)

    def getConnects(self):
        self.createConnects()
        return self.connections







