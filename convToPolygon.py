from edger import edgeFinder
from helpers import *
from surveyor import surveyor
from illustrator import Illustrator
from shaper import Shaper
import skimage.morphology as labeler


#SETUP OUR LOCATION
location = getLocation(locChoice = 'vi')
path = 'Locations/%s/' % location['name']
config = importYaml(path + 'config')
filename = (path + "terrain")

#SETUP HEIGHTMAP
mapper = surveyor(location['name'], location['bounds']['north'], location['bounds']['south'], location['bounds']['east'], location['bounds']['west'])
mapper.setQuality(16)
mapper.scan()

#SETUP EDGER
edger = edgeFinder(mapper.getNpGrid())
edger.markEdges(1)
edges = edger.edges

#SETUP PDF CANVAS
canvas = Illustrator(filename, edger.width, edger.height)

#DEBUG: draw the edges as a background
saveAsImage(convertToImage(edges), filename)
canvas.drawPNGFile(filename, -0.5, -0.5)

#SETUP SHAPER
shapey = Shaper(edges)



#START WORK
#shapey.groupPoints()
#shapey.createShapes()
#shapey.sortShapes()
#canvas.drawPixels(edger.edgePoints())
lines = shapey.getConnections()
canvas.drawLines(lines)

#canvas.drawShapes(shapey.shapes)
#canvas.drawPoints(shapey.getCenters())


#SAVE A COPY
canvas.save()