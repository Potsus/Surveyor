import numpy as np 
import math
from helpers import *
from geopy.distance import VincentyDistance as distance
from location import locationFromName



def sizeAtDPI(location, dpi):
    center = findCenter(location)


def findCenter(location):
    latitude  = location.north + ((location.north - location.south)/2)
    longitude = location.east  + ((location.east  - location.west) /2)
    return (latitude, longitude)


def getTick():
    NORTH = 18.538608
    EAST  = -64.316278
    SOUTH = 18.289912
    WEST  = -65.107491

    FEET_IN_MILE = 5280

    WALL_WIDTH = 7
    WALL_WIDTH_MAX = 8
    WALL_HEIGHT_MAX = 4

    TOP_RIGHT    = (NORTH, EAST)
    TOP_LEFT     = (NORTH, WEST)
    BOTTOM_RIGHT = (SOUTH, EAST)
    BOTTOM_LEFT  = (SOUTH, WEST)

    TOP_DIST    = distance(TOP_RIGHT, TOP_LEFT).miles
    BOTTOM_DIST = distance(BOTTOM_RIGHT, BOTTOM_LEFT).miles
    LEFT_DIST   = distance(TOP_LEFT, BOTTOM_LEFT).miles
    RIGHT_DIST  = distance(TOP_RIGHT, BOTTOM_RIGHT).miles


    #print('Top Width: %s Miles' % TOP_DIST)
    #print('Bottom Width: %s Miles' % BOTTOM_DIST)
    #print('Left Height: %s Miles' % LEFT_DIST)
    #print('Right Height: %s Miles' % RIGHT_DIST)

    WIDTH_HEIGHT_RATIO = TOP_DIST/LEFT_DIST
    #print('Width to Height Ratio: %s' % WIDTH_HEIGHT_RATIO)

    HEIGHT_WIDTH_RATIO = LEFT_DIST/TOP_DIST
    #print('Height to Width Ratio: %s' % HEIGHT_WIDTH_RATIO)

    WALL_HEIGHT = WALL_WIDTH/WIDTH_HEIGHT_RATIO
    #print('Approximate Wall Dimensions: %s x %s' % (feetReadable(WALL_WIDTH), feetReadable(WALL_HEIGHT)))

    if WALL_HEIGHT > WALL_HEIGHT_MAX:
    	print('Wall height exceeds max by %s' % (feetReadable(WALL_HEIGHT - WALL_HEIGHT_MAX)))

    if WALL_WIDTH > WALL_WIDTH_MAX:
    	print('Wall height exceeds max by %s ft' % (feetReadable(WALL_WIDTH - WALL_WIDTH_MAX)))

    SCALE = (TOP_DIST * FEET_IN_MILE) / WALL_WIDTH

    #print('Approximate Scale: 1/%sth' % int(SCALE))

    #print('1 mile is approx %s at current scale' % (feetReadable(scaleBigToSmall(SCALE, FEET_IN_MILE))))

    #get the ratio of 8th decimal point lat and lng to scaled size
    TICK = 0.00001569
    #DESIRED_RESOLUTION should be the clarity we want at fabrication, here its in samples per inch
    #DESIRED_RESOLUTION = 600

    #TICK_DIST = distance((NORTH, EAST), (NORTH, EAST + TICK))

    #Samples per mile
    #DESIRED_RESOLUTION * feetReadable(scaleBigToSmall(SCALE, FEET_IN_MILE))

    #lng difference per mile at location

    #print('%s is about %s feet' % (TICK, TICK_DIST.miles * FEET_IN_MILE))
    #
    #
    #
    #
    #TICK_SCALE = scaleBigToSmall(SCALE, TICK_DIST.miles * FEET_IN_MILE)
    #TICK_SCALED_INCHES = TICK_SCALE * 12
    #RESOLUTION = 1/TICK_SCALED_INCHES
    #print('meaning our clarity is roughly %s dpi' % math.floor(RESOLUTION))
    #
    #
    ##dpi to dots per foot, dpf
    ##foot scaled to miles, dpm
    #
    #TICKS_PER_MILE = 1/TICK_DIST.miles
    #DESIRED_TICK = 0
    #DDPM = (DESIRED_RESOLUTION * 12 * FEET_IN_MILE)


    #print('ticks per mile: %s' % TICKS_PER_MILE)

    #print('going backwards, a desired resolution of %s dpi has a tick size %s' % (DESIRED_RESOLUTION, DESIRED_TICK))


