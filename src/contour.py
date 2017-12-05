import shapefile 
from illustrator import Illustrator
from helpers import *

print('in contour')

print('importing location')

locations = importYaml('locations')
loc   = locations['vi']
north = loc['bounds']['north']
south = loc['bounds']['south']
east  = loc['bounds']['east']
west  = loc['bounds']['west']

root = 'SRTM/vi10'
file = '%s/contour.shp' % root
out  = '%s/preview' % root

ew = abs(east-west)
ns = abs(north-south)

print('ns: %s, ew: %s' % (ns, ew))


contours = shapefile.Reader(file)
shapes = contours.shapes()
print('found %s shapes' % len(shapes))

width = 6304
height = 1982

canvas = Illustrator(out, width, height)

def latToX(lat):
    return abs(((lat - west)/ew)*width)

def lonToY(lon):
    return abs(((lon - north)/ns)*height)

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

    #print('drawing shape')
    canvas.drawLineRed(points)


print('drawing shapes')
for shape in shapes:
    if shape.shapeType == 5:
        #print('found a ploygon')
        printShape(shape)
    if shape.shapeType == 3:
        #print('found a line')
        #if shape.bbox
        printLine(shape)

print('saving picture')
canvas.save()


