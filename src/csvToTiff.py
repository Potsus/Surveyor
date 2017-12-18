from modules.helpers import loadCsv
from modules.location import locationFromName

#import georasters as gr
import numpy as np
from osgeo import gdal
from osgeo import gdal_array
from osgeo import osr

print('in converter')

print('importing location')

loc = locationFromName('The_Virgin_Islands')

rawfile = '6304x1982'

data = loadCsv(loc.rawdir+rawfile)

#prep the data to load the csv as a tiff

print('preping data')

width  = len(data[0])
height = len(data)

filename = loc.root + 'geo'

#ma = np.ma.masked_array(data)
array = np.array(data)

pixwidth = (loc.west - loc.east)/width
pixheight = (loc.north - loc.south)/height

geot = (loc.west, pixwidth, 0.0, loc.north, 0.0, pixheight)

print('creating raster')

#raster = gr.GeoRaster(ma, geot)
output_raster = gdal.GetDriverByName('GTiff').Create(filename+'.tif',width, height, 1 ,gdal.GDT_Float32)
output_raster.SetGeoTransform(geot)
srs = osr.SpatialReference()                 # Establish its coordinate encoding
srs.ImportFromEPSG(4326)  

output_raster.SetProjection( srs.ExportToWkt() )   # Exports the coordinate system 
                                                   # to the file

print('saving tiff')
#raster.to_tiff(filename)
output_raster.GetRasterBand(1).WriteArray(array)   # Writes my array to the raster
