#Save locations to the django model
from subprocess import Popen
from location import Location
from helpers import *
#from os import getcwd


def getSRTMArea(location, version=1):

    #The --bounds option accepts latitude and longitude coordinates (more precisely in geodetic coordinates in the WGS84 refernce system EPSG:4326 for those who care) given as left bottom right top similarly to the rio command form rasterio.
    #NAME, LEFT, BOTTOM, RIGHT, TOP
    #set the version to download with --product SRTM1 | SRTM3
    command = [
        'eio', #the elevation prog
        '--product',
        'SRTM'+str(version),
        'clip', #clip operation
        '-o', #output flag
        str(location.tiff), #output filename
        '--bounds', #bounded 
        str(location.west), 
        str(location.south), 
        str(location.east), 
        str(location.north) 
    ]

    #print(' '.join(command))

    p = Popen(command)
    p.wait()

#this will generate a contour at height intervals so you don't have to run it a bunch of times
#there is a -3d flag you can set to get the height for each point in the contour that i probably want
#offset tells it where to start the contours
#z flips the flag for 3d points
def generateContours(input, output_dir, height=10, offset=None, z=False, voids=False):
    remove_dir(output_dir)

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

    args.append(input)
    args.append(output_dir)

    print(args)
    p = Popen(args)
    p.wait()

#ostensibly to import the contours to a postgres database
#i think i can write something that doesn't require console commands and the db on the same server
def postgisImportContours(filename):

    call(['shp2pgsql', '-p', '-I', '-g', 'way', '-s', '4326:900913', filename, 'contour', '|', 'psql', '-h', 'localhost', '-p', '5432', '-U', 'postgres', '-d', 'gis'])

    call(['shp2pgsql', '-a', '-g', 'way', '-s', '4326:900913', filename, 'contour', '|', 'psql', '-h', 'localhost', '-p', '5432', '-U', 'postgres', '-d', 'gis'])

