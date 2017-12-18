import shapefile 
from modules.illustrator import Illustrator
from modules.SRTM import SRTM
from modules.location import locationFromName


print('in contour')

print('importing location')

loc = locationFromName('The_Virgin_Islands')
#loc = locationFromName('Amsterdam')

contoursdir = loc.contoursdir
#tiff = loc.root + loc.tiff
tiff = loc.root + 'geo.tif'
cutoff = 6

getSRTMArea(loc, version=3) #fetch the relevant areas and clip them to our bounds

generateContours(tiff, contoursdir ,height=25, z=True) #use the tiff we generated to generate shp files



#file = loc.contoursdir + 'contour.shp'
file = loc.root + 'gmapscontours/' + 'contour.shp'
out  = loc.root + 'contours' 

#def contoursToShapes(folder)




ew = abs(loc.east-loc.west)
ns = abs(loc.north-loc.south)

print('ns: %s, ew: %s' % (ns, ew))


contours = shapefile.Reader(file)
shapes = contours.shapes()
print('found %s shapes' % len(shapes))

width = 6304
height = 1982

canvas = Illustrator(out, width, height)

def latToX(lat):
    return abs(((lat - loc.west)/ew)*width)

def lonToY(lon):
    return abs(((lon - loc.north)/ns)*height)

def convPoint(point):
    y = latToX(point[0])
    x = lonToY(point[1])
    #print('point: (%s,%s)' % (x,y))
    return (x,y)

def printShape(shape):
    points = []
    for point in shape.points:
        points.append(convPoint(point))

    #print('drawing shape')
    canvas.drawShape(points)

def printLine(line):
    points = []
    for point in line.points:
        points.append(convPoint(point))

    points = cleanupShape(points)
    #print('drawing line')
    canvas.drawLine(points)




from scipy.interpolate import splprep, splev
import numpy as np

def padEnds(shape):
    shape.append(shape[0])
    shape.append(shape[1])
    return shape    

def clipEnds(shape):
    shape.pop()
    shape.pop()
    return shape

def smoothShape(shape, s=3.0, k=2, f=0.5):
    #print('creating smooth shape # of length %s' % len(shape))
    # Smoothing the shape.
    # spline parameters
    #s = 5.0 # smoothness parameter
    #k = 2 # spline order
    #nest = -1 # estimate of number of knots needed (-1 = maximal)
    #f = 4 #how many samples you want to reduce by

    try:
        #print('unzipping shape')
        x,y = zip(*shape)
        if len(x) < 10:
            return shape
        #print('splprep')
        t, u = splprep([x, y], s=s, k=k, nest=-1)
        #print('splprep finished')

        #determine the reduction factor by how many points there are
        samples = int(len(x)/f)
        if  samples <= 3:
            samples = len(shape)*3

        #print('taking %s samples' % samples)

        xn, yn = splev(np.linspace(0, 1, samples), t)  
        print('splev finished')
        return zip(xn, yn)
    except:
        #print('failed')
        return shape   

def cleanupShape(shape):
    #shape = padEnds(shape)
    #shape = smoothShape(shape)
    #shape = clipEnds(shape)
    return shape



print('drawing shapes')
for shape in shapes:
    #print('shape type: %s' % shape.shapeType)
    if shape.z[0] < cutoff:
        continue
    if shape.shapeType == 5 or shape.shapeType == 15:
        #print('found a ploygon')
        printShape(shape)
    if shape.shapeType == 3 or shape.shapeType == 13:
        #print('found a line')
        #if shape.bbox
        printLine(shape)

print('saving picture')
canvas.save()


