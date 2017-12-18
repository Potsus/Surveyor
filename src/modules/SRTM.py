#Save locations to the django model
from subprocess import Popen
from location import Location
from helpers import *
from os import getcwd

class SRTM:

    def __init__(self, location):
        self.location = location
        self.cwd = "%s/%s" % (getcwd(), self.location.root) #get around gdal having problems with space in the name, didn't work

    def getArea(self, version=1):

        #The --bounds option accepts latitude and longitude coordinates (more precisely in geodetic coordinates in the WGS84 refernce system EPSG:4326 for those who care) given as left bottom right top similarly to the rio command form rasterio.
        #NAME, LEFT, BOTTOM, RIGHT, TOP
        #set the version to download with --product SRTM1 | SRTM3
        command = [
            'eio', #the elevation prog
            '--product',
            'SRTM'+str(version),
            'clip', #clip operation
            '-o', #output flag
            str(self.location.tiff), #output filename
            '--bounds', #bounded 
            str(self.location.west), 
            str(self.location.south), 
            str(self.location.east), 
            str(self.location.north) 
        ]

        print('cwd: ' + self.cwd)
        print(' '.join(command))

        p = Popen(command, cwd=self.cwd)
        p.wait()

    #this will generate a contour at height intervals so you don't have to run it a bunch of times
    #there is a -3d flag you can set to get the height for each point in the contour that i probably want
    #offset tells it where to start the contours
    #z flips the flag for 3d points
    def generateContours(self, height=10, offset=None, z=False, voids=False):
        remove_dir(self.location.contoursdir)

        args = []
        args.append('gdal_contour')
        if height:
            args.append('-i')
            args.append(str(height))

        if z == True:
            args.append('-3d')

        args.append('-a')
        args.append('height')

        args.append('-inodata')

        if offset != None:
            args.append('-off')
            args.append(str(offset))

        args.append(self.location.tiff)
        args.append(self.location.contours)

        print(args)
        p = Popen(args, cwd=self.cwd)
        p.wait()


    #ostensibly to import the contours to a postgres database
    #i think i can write something that doesn't require console commands and the db on the same server
    def importContours(self):
        filename = '%s/contour.shp' % self.contours

        call(['shp2pgsql', '-p', '-I', '-g', 'way', '-s', '4326:900913', filename, 'contour', '|', 'psql', '-h', 'localhost', '-p', '5432', '-U', 'postgres', '-d', 'gis'])

        call(['shp2pgsql', '-a', '-g', 'way', '-s', '4326:900913', filename, 'contour', '|', 'psql', '-h', 'localhost', '-p', '5432', '-U', 'postgres', '-d', 'gis'])
