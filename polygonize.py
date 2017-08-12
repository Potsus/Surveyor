import cairocffi as cairo 
from edger import edgeFinder
from helpers import *



path = 'Locations/Mosquito Island/'

config = importYaml(path + 'config')

heightmap = np.load(path+'heightmap.npy')
#heightmap = np.fliplr(heightmap)
edger = edgeFinder(heightmap)

points = edger.pointsAtDepth(10)


#you have to order the points by their place in the shape
#NEXT
shapes = []

colors = [(0,0,0),(1,0,0),(0,1,0),(0,0,1), (1,1,0), (1,0,1), (0,1,1)]
color = 0






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
        if not closeShape(curPoint):
            if not closePoint(curPoint):
                print('lone point')
                shapes.append([curPoint])

def orderPointsOld():
    while points:
        #points will get popped in odd places and many shapes will be made that should be joined
        curPoint = points.pop()
        if not closeShapeOld(curPoint):
            if not closePointOld(curPoint):
                print('lone point')
                shapes.append([curPoint])


def closePoint(curPoint):
    buds = closeBuds(curPoint)
    for bud in buds:
        i = locInList(bud, points)
        if i != False:
            shapes.append([curPoint, points.pop(i)])
            return True

    return False

def closePointOld(curPoint):
    buds = closeBudsOld(curPoint)
    for bud in buds:
        i = locInList(bud, points)
        if i != False:
            shapes.append([curPoint, points.pop(i)])
            return True

    return False

def closeBuds(curPoint):
    x,y = curPoint
    #remember that the axes are reversed
    return edger.orderedBuds(x,y)

def closeBudsOld(curPoint):
    x,y = curPoint
    #remember that the axes are reversed
    return edger.buds(x,y)

def closeShape(curPoint):
    buds = closeBuds(curPoint)
    for i in range(0, len(shapes)):
        for bud in buds:
            if bud == shapes[i][0]:
                shapes[i].insert(0, curPoint)
                return True
            elif bud == shapes[i][-1]:
                shapes[i].append(curPoint)
                return True
    return False

def closeShapeOld(curPoint):
    buds = closeBudsOld(curPoint)
    for i in range(0, len(shapes)):
        for bud in buds:
            if bud == shapes[i][0]:
                shapes[i].insert(0, curPoint)
                return True
            elif bud == shapes[i][-1]:
                shapes[i].append(curPoint)
                return True
    return False





def locInList(needle, haystack):
    try:
        i = haystack.index(needle)
        return i
    except ValueError:
        return False


def joinShapes():
    for i in range(0, len(shapes)):
        #print('checking from the front')
        buds = closeBuds(shapes[i][0])
        for j in range(0, len(shapes)):
            if j == i:
                continue
            for bud in buds:
                if bud == shapes[j][-1]:
                    #front of shape i, back of shape j
                    #append i to j
                    shapes[j].extend(shapes.pop(i))
                    #print('joining shapes %s and %s at point %s' % (i, j, bud))
                    return False
                elif bud == shapes[j][0]: 
                    #front of i front of j
                    #reverse i and append j
                    shapes[i].reverse()
                    shapes[i].extend(shapes.pop(j))
                    #print('joining shapes %s and %s at point %s' % (i, j, bud))
                    return False
        #print('checking from the back')
        buds = closeBuds(shapes[i][-1])
        for j in range(0, len(shapes)):
            if j == i:
                continue
            for bud in buds:
                if bud == shapes[j][-1]:
                    #back of shape i, back of shape j
                    #i gets reversed and added to back of j
                    shapes[i].reverse()
                    shapes[j].extend(shapes.pop(i))
                    #print('joining shapes %s and %s at point %s' % (i, j, bud))
                    return False
                elif bud == shapes[j][0]:
                    #back of shape i, front of shape j
                    #j goes on the back of i
                    shapes[i].extend(shapes.pop(j))
                    #print('joining shapes %s and %s at point %s' % (i, j, bud))
                    return False


    return True

#def fixEnds()

def numPoints():
    total = 0
    for shape in shapes:
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
    for i in range(0, len(shapes)):
        for j in range(1, len(shapes[i])-1):
            if shapes[i][j][0] == shapes[i][j-1][0] and shapes[i][j][0] == shapes[i][j+1][0]:
                rotateShapeTo(i,j)
                return True


def rotateShapeTo(shapeIndex, i):
    print('rotating shape end to %s' % i)
    fragment1 = shapes[shapeIndex][:i-1] 
    fragment2 = shapes[shapeIndex][i-1:]
    shapes[shapeIndex] = fragment2 + fragment1   

def padEnds():
    for i in range(0, len(shapes)):
        shapes[i].append(shapes[i][0])    
        shapes[i].append(shapes[i][1]) 

def clipEnds():
    for i in range(0, len(shapes)):
        shapes[i].pop()
        shapes[i].pop()

def cleanupShapes():
    while not joinShapes():
        print("%s shapes, %s points total" % (len(shapes), numPoints()))

    fixEnds()

    padEnds()

    for i in range(0, len(shapes)):
        shapes[i] = smoothShape(shape=shapes[i], s=80)
        #shapes[i].reverse()

    clipEnds()
    





orderPoints()
#orderPointsOld()

cleanupShapes()

#smoo = smoothShape(80)
#shapes.append(smoo)

filename = (path + "terrain")

surface = cairo.PDFSurface ((filename+'.pdf'), edger.width, edger.height)
cr = cairo.Context(surface)

def drawShapesToFile(filename):

    surface = cairo.PDFSurface ((filename+'.pdf'), edger.width, edger.height)
    cr = cairo.Context(surface)

    for shape in shapes:
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


drawShapesToFile(filename)

surface.finish()