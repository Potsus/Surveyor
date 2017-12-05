#Save locations to the django model
from helpers import importYaml
from subprocess import call

class SRTM:
    locations = importYaml('locations')

    def __init__(self, selector):
        self.selector = selector
        self.location = self.locations['selector']
        self.north = self.location['bounds']['north']
        self.south = self.location['bounds']['south']
        self.east  = self.location['bounds']['east']
        self.west  = self.location['bounds']['west']

        self.root = 'SRTM'
        self.tiff = '%s/%s.tiff' % (self.root, self.name)
        self.contours = '%s/contours' % root 

    def getArea(self):

        #The --bounds option accepts latitude and longitude coordinates (more precisely in geodetic coordinates in the WGS84 refernce system EPSG:4326 for those who care) given as left bottom right top similarly to the rio command form rasterio.
        #NAME, LEFT, BOTTOM, RIGHT, TOP
        command = [
            'eio', #the elevation prog
            'clip', #clip operation
            '-o', #output flag
            self.tiff, #output filename
            '--bounds', #bounded 
            str(self.west), 
            str(self.south), 
            str(self.east), 
            str(self.north) 
        ]

        call(command)

    def generateContours(self, height):
        call(['gdal_contour', '-i', str(height), '-a', 'height', self.tiff, self.contours])


    def importContours(self):
        filename = '%s/contour.shp' % self.contours

        call(['shp2pgsql', '-p', '-I', '-g', 'way', '-s', '4326:900913', filename, 'contour', '|', 'psql', '-h', 'localhost', '-p', '5432', '-U', 'postgres', '-d', 'gis'])

        call(['shp2pgsql', '-a', '-g', 'way', '-s', '4326:900913', filename, 'contour', '|', 'psql', '-h', 'localhost', '-p', '5432', '-U', 'postgres', '-d', 'gis'])




#for key, place in locations.iteritems():
#    loc = Location(name = place['name'], north = place['bounds']['north'], south = place['bounds']['south'], east  = place['bounds']['east'], west  = place['bounds']['west'])
#    loc.save()

loc = SRTM('vi')

#loc.getArea()
#loc.generateContours()
#loc.importContours()