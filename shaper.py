import cairocffi as cairo 
from edger import edgeFinder
from helpers import *
from scipy.interpolate import splprep, splev
import sys
import math

#TODO: actually figure out what the water level is

class Shaper:

    colors = [(0,0,0),(1,0,0),(0,1,0),(0,0,1), (1,1,0), (1,0,1), (0,1,1)]
    color = 0

    def __init__(self, data):
        self.data = data
        self.edger = edgeFinder(data)

        self.shapes = []
        self.points = []
        self.drawables = []


    def nextColor(self):
        if self.color == len(self.colors)-1:
            self.color = 0
        else:
            self.color += 1

    def orderPoints(self):
        while self.points != []:
            #points will get popped in odd places and many shapes will be made that should be joined
            curPoint = self.points.pop()
            if not self.closeShape(curPoint):
                if not self.closePoint(curPoint):
                    print('lone point')
                    self.shapes.append([curPoint])


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

    def joinShapes(self):
        for i in range(0, len(self.shapes)):
            if type(self.shapes[i]) == tuple or len(self.shapes[i]) == 1:
                print('attempting mid shape insert')
                if self.midShape(self.shapes[i][0]):
                    self.shapes.pop(i)
                    return False
                continue
            #print('checking from the front')
            buds = self.closeBuds(self.shapes[i][0])
            for j in range(0, len(self.shapes)):
                if j == i:
                    continue
                for bud in buds:
                    if bud == self.shapes[j][-1]:
                        #front of shape i, back of shape j
                        #append i to j
                        self.shapes[j].extend(self.shapes.pop(i))
                        #print('joining self.shapes %s and %s at point %s' % (i, j, bud))
                        return False
                    elif bud == self.shapes[j][0]: 
                        #front of i front of j
                        #reverse i and append j
                        self.shapes[i].reverse()
                        self.shapes[i].extend(self.shapes.pop(j))
                        #print('joining self.shapes %s and %s at point %s' % (i, j, bud))
                        return False
            #print('checking from the back')
            buds = self.closeBuds(self.shapes[i][-1])
            for j in range(0, len(self.shapes)):
                if j == i:
                    continue
                for bud in buds:
                    if bud == self.shapes[j][-1]:
                        #back of shape i, back of shape j
                        #i gets reversed and added to back of j
                        self.shapes[i].reverse()
                        self.shapes[j].extend(self.shapes.pop(i))
                        #print('joining self.shapes %s and %s at point %s' % (i, j, bud))
                        return False
                    elif bud == self.shapes[j][0]:
                        #back of shape i, front of shape j
                        #j goes on the back of i
                        self.shapes[i].extend(self.shapes.pop(j))
                        #print('joining self.shapes %s and %s at point %s' % (i, j, bud))
                        return False
        return True

    #def fixEnds()

    def numPoints(self):
        total = 0
        for shape in self.shapes:
            total += len(shape)
        return total

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
        

    def drawShapesToFile(self, filename):

        self.surface = cairo.PDFSurface ((filename+'.pdf'), self.edger.width, self.edger.height)
        self.cr = cairo.Context(self.surface)

        while self.drawables:
            self.drawShape(self.drawables.pop())

    def drawShape(self, points):
        if type(points) == tuple:
            #its a point, draw a circle i guess?
            self.drawPoint(points)
            return

        if len(points) == 1:
            #its a point, draw a circle i guess?
            self.drawPoint(points[0])
            return

        if len(points) == 0:
            return

        print('drawing shape length %s' % len(points))

        self.cr.set_source_rgb(*self.colors[self.color])
        self.cr.set_line_join(cairo.LINE_JOIN_ROUND)
        self.cr.set_line_cap(cairo.LINE_CAP_ROUND)
        self.cr.set_line_width(.1)


        start = points.pop(0)
        #remember that the axes are reversed
        self.cr.move_to(start[1], start[0])

        for point in points:
            self.cr.line_to(point[1], point[0])
        self.points.append(start)
        self.cr.close_path()
        self.cr.stroke()
        self.nextColor()

    def drawPoint(self, point):
        print('drawing point %s, %s' % point)
        self.cr.set_source_rgb(*self.colors[self.color])
        self.cr.set_line_join(cairo.LINE_JOIN_ROUND)
        self.cr.set_line_cap(cairo.LINE_CAP_ROUND)
        self.cr.set_line_width(.1)
        self.cr.arc(point[1], point[0], 0.2, 0, 2*math.pi)
        self.cr.stroke()
        self.nextColor()


    def getPointsAtDepth(self, depth):
        self.points = self.edger.pointsAtDepth(depth)

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




path = 'Locations/Mosquito Island/'
filename = (path + "terrain")

#surface = cairo.PDFSurface ((filename+'.pdf'), edger.width, edger.height)
#cr = cairo.Context(surface)

heightmap = np.load(path+'heightmap.npy')
shapey = Shaper(heightmap)
try:
    shapey.createRing(60)
    #shapey.createRings(10, 5)
except Exception, err:
    sys.stderr.write('ERROR: %sn' % str(err))
    #print sys.exc_info()[0]
    shapey.drawables.extend(shapey.shapes)

shapey.drawShapesToFile(filename)

shapey.surface.finish()