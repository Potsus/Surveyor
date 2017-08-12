import cairocffi as cairo 
from edger import edgeFinder
from helpers import *

class Shaper:

    colors = [(0,0,0),(1,0,0),(0,1,0),(0,0,1), (1,1,0), (1,0,1), (0,1,1)]
    color = 0

    def __init__(self, data):
        
    self.edger = edgeFinder(data)

    #self.points = edger.pointsAtDepth(10)


    self.shapes = []




    def nextColor():
        global color
        if color == len(colors)-1:
            color = 0
        else:
            color += 1

    def orderPoints():
        while points:
            #points will get popped in odd places and many shapes will be made that should be joined
            curPoint = points.pop()
            if not self.closeShape(curPoint):
                if not self.closePoint(curPoint):
                    print('lone point')
                    self.shapes.append([curPoint])


    def closePoint(curPoint):
        buds = self.closeBuds(curPoint)
        for bud in buds:
            i = locInList(bud, points)
            if i != False:
                self.shapes.append([curPoint, points.pop(i)])
                return True

        return False

    def closeBuds(curPoint):
        x,y = curPoint
        #remember that the axes are reversed
        return self.edger.orderedBuds(x,y)

    def closeShape(curPoint):
        buds = closeBuds(curPoint)
        for i in range(0, len(self.shapes)):
            for bud in buds:
                if bud == self.shapes[i][0]:
                    self.shapes[i].insert(0, curPoint)
                    return True
                elif bud == self.shapes[i][-1]:
                    self.shapes[i].append(curPoint)
                    return True
        return False

    def locInList(needle, haystack):
        try:
            i = haystack.index(needle)
            return i
        except ValueError:
            return False


    def joinShapes():
        for i in range(0, len(self.shapes)):
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

    def numPoints():
        total = 0
        for shape in self.shapes:
            total += len(shape)
        return total

    def smoothShape(shape, s=5, k=2, f=4):
        print('creating smooth shape')
        from scipy.interpolate import splprep, splev
        # Smoothing the shape.
        # spline parameters
        #s = 5.0 # smoothness parameter
        #k = 2 # spline order
        #nest = -1 # estimate of number of knots needed (-1 = maximal)
        #f = 4 #how many samples you want to reduce by

        x,y = zip(*shape)
        t, u = splprep([x, y], s=s, k=k, nest=-1)
        samples = int(len(x)/f)
        xn, yn = splev(np.linspace(0, 1, samples), t)  
        return zip(xn, yn)     

    def fixEnds():
        for i in range(0, len(self.shapes)):
            for j in range(1, len(self.shapes[i])-1):
                if self.shapes[i][j][0] == self.shapes[i][j-1][0] and self.shapes[i][j][0] == self.shapes[i][j+1][0]:
                    rotateShapeTo(i,j)
                    return True


    def rotateShapeTo(shapeIndex, i):
        print('rotating shape end to %s' % i)
        fragment1 = self.shapes[shapeIndex][:i-1] 
        fragment2 = self.shapes[shapeIndex][i-1:]
        self.shapes[shapeIndex] = fragment2 + fragment1   

    def padEnds():
        for i in range(0, len(self.shapes)):
            self.shapes[i].append(self.shapes[i][0])    
            self.shapes[i].append(self.shapes[i][1]) 

    def clipEnds():
        for i in range(0, len(self.shapes)):
            self.shapes[i].pop()
            self.shapes[i].pop()

    def cleanupShapes():
        while not joinShapes():
            print("%s self.shapes, %s points total" % (len(self.shapes), numPoints()))

        fixEnds()

        padEnds()

        for i in range(0, len(self.shapes)):
            self.shapes[i] = smoothShape(shape=self.shapes[i], s=80)
            #self.shapes[i].reverse()

        clipEnds()
        

    def drawShapesToFile(filename):

        surface = cairo.PDFSurface ((filename+'.pdf'), edger.width, edger.height)
        cr = cairo.Context(surface)

        for shape in self.shapes:
            drawShape(shape)

    def drawShape(points):
        print('drawing shape length %s' % len(points))

        cr.set_source_rgb(*colors[color])
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_line_width(.1)


        start = points.pop(0)
        #remember that the axes are reversed
        cr.move_to(start[1], start[0])

        for point in points:
            cr.line_to(point[1], point[0])
        points.append(start)
        cr.close_path()
        cr.stroke()
        nextColor()
        

orderPoints()
#orderPointsOld()

cleanupShapes()

#smoo = smoothShape(80)
#self.shapes.append(smoo)

filename = (path + "terrain")

surface = cairo.PDFSurface ((filename+'.pdf'), edger.width, edger.height)
cr = cairo.Context(surface)

drawShapesToFile(filename)

surface.finish()