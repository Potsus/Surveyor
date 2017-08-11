import numpy as np 
from helpers import *

class edger:

    def __init__(self, data)
    self.data = data
    
    self.height, self.width = data.shape

    self.edges = np.zeros((height, width))   

    #get all neighbors of a given point
    #the naming is super fucky here because of the different way coords and array coords work
    self.buds = lambda x, y : [(x2, y2) for x2 in range(x-1, x+2)
       for y2 in range(y-1, y+2)
       if (-1 < x <= self.height and
           -1 < y <= self.width and
           (x != x2 or y != y2) and
           (0 <= x2 <= self.height-1) and
           (0 <= y2 <= self.width-1))] 


    def markEdges(self):
        #print('creating edge map')
        for y in range(0, (self.height)):
            for x in range(0, (self.width)):
                #out = 'x: %s, y: %s' % (x,y)
                if checkEdge(x,y):
                    self.edges[y][x] = 1
                    #out += '  edge'
                #print out


    def checkEdge(self, x, y):
        #if there's no value there it can't be an edge
        if self.clipped[y][x] == 0:
            return False

        #check all the neighbors for 
        for bud in self.buds(y,x):
            if self.clipped[bud[0], bud[1]] == 0:
                return True
        return False



    def edgePointsAtDepth(self, depth):

        self.clipped = np.clip(self.data, depth, depth + 1)
        self.clipped = self.clipped - depth


        self.markEdges()

        #showImage(edges)

        #get the nonzero points
        #returns two arrays of indicies, kinda inconvienient
        xs, ys = edges.nonzero()

        #combine arrays of indices into a list of tuples
        points = zip(xs, ys)

        return points