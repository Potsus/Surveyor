import numpy as np
from helpers import *


class Slicer:

    def __init__(self, data):

        self.data = convertToArray(data)

    def cleanSlice(self, data, lower, upper, prefix):
        data = np.clip(data, lower, upper)
        suffix = ('%s-%s' % (lower, upper))
        print('generating image with bounds %s' % suffix)
        saveAsImage(data, self.slicesdir + '%s %s %s' % (prefix, self.filename, suffix))

    def generateCleanCuts(self, minimum, layerHeight):
        numLayers = int((self.data.max() - minimum)/layerHeight)
        empty_dir(self.slicesdir)
        for i in range(0, numLayers):
            upper = (minimum + (layerHeight * (i+1)))
            lower = (minimum + (layerHeight * i))
            self.cleanSlice(self.data, lower, upper, str(i).zfill(4))
            i = i+1

