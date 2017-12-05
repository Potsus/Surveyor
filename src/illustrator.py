import cairocffi as cairo
from helpers import *

#provides easy methods to draw shapes, images and other shit to a pdf

class Illustrator:
    #colors to use when drawing
    colors = [(1,0,0),(0,1,0),(0,0,1), (1,1,0), (1,0,1),(0,1,1),(.5,0,0),(0,.5,0),(0,0,.5),(.5,.5,0),(.5,0,.5),(0,.5,.5),(.5,.5,.5)]

    def __init__(self, filename, width, height):

        #SETUP THE CANVAS
        self.width = width
        self.height = height
        self.filename = filename
        self.clearCanvas()
        self.cr = cairo.Context(self.surface)

        #the current color to use
        self.color = 0

    def clearCanvas(self):
        self.surface = cairo.PDFSurface ((self.filename+'.pdf'), self.width, self.height)

    def nextColor(self):
        if self.color == len(self.colors)-1:
            self.color = 0
        else:
            self.color += 1

    def drawShapes(self, shapes):
        for shape in shapes:
            self.drawShape(shape)

    def drawShape(self, points):
        #TODO: maybe move this error checking out of drawShape
        if type(points) == tuple:
            #its a point, draw a circle i guess?
            self.drawPoint(points)
            return

        if len(points) == 1:
            #its a point, draw a circle i guess?
            self.drawPoint(points[0])
            return

        if len(points) == 0:
            return

        print('drawing shape length %s' % len(points))
        self.setupLine()

        
        start = points.pop(0) #move to the first point and make sure not to repeat it
        self.cr.move_to(start[1], start[0]) #remember that the axes are reversed

        for point in points:
            self.cr.line_to(point[1], point[0])
        
        points.append(start) #TODO: is this necessary? 
        self.cr.close_path() #close the shape
        self.cr.stroke() #actually color the line we drew


    def drawPoint(self, point):
        print('drawing point %s, %s' % point)
        #set all the line settings
        self.setupLine()
        self.cr.set_line_width(.5)
        self.cr.fill()
        self.cr.arc(point[1], point[0], 2, 0, 2*math.pi)
        self.cr.stroke()

    def drawPoints(self, points):
        for point in points:
            self.drawPoint(point)

    def drawPixels(self, points):
        for point in points:
            self.drawPixel(point)

    def drawPixel(self, point):
        self.cr.set_source_rgb(0,0,0)
        print("drawing rectangle with coords: %s %s %s %s" %(point[1]-0.5, point[0]-0.5, point[1]+0.5, point[0]+0.5))
        self.cr.rectangle(point[1]-0.5, point[0]-0.5, point[1]+0.5, point[0]+0.5)
        self.cr.set_line_width(0.05)
        self.cr.set_line_join(cairo.LINE_CAP_ROUND)
        self.cr.stroke_preserve()
        self.cr.set_source_rgb(1, 1, 1)
        self.cr.fill()

    def drawLines(self, lines):
        for line in lines:
            self.drawLine(line)

    def drawLineRed(self, line):
        self.cr.set_source_rgb(1,0,0)
        self.cr.set_line_width(0.2)
        self.cr.set_line_join(cairo.LINE_JOIN_ROUND)
        self.cr.set_line_cap(cairo.LINE_CAP_ROUND)
        start = line.pop(0) #move to the first point and make sure not to repeat it
        self.cr.move_to(start[1], start[0]) #remember that the axes are reversed

        for point in line:
            self.cr.line_to(point[1], point[0])

        self.cr.stroke()

    def drawLine(self, line):
        self.setupLine()
        start = line.pop(0) #move to the first point and make sure not to repeat it
        self.cr.move_to(start[1], start[0]) #remember that the axes are reversed

        for point in line:
            self.cr.line_to(point[1], point[0])

        self.cr.stroke()

    def setupLine(self):
        self.cr.set_source_rgb(*self.colors[self.color])
        self.cr.set_line_join(cairo.LINE_JOIN_ROUND)
        self.cr.set_line_cap(cairo.LINE_CAP_ROUND)
        self.cr.set_line_width(.5)
        self.nextColor() #don't draw the next line the same color

    def drawPNGFile(self, filename, x, y):
        img = cairo.ImageSurface.create_from_png('%s.png' % filename)
        self.cr.set_source_surface(img, x, y) 
        self.cr.paint()

    def drawPNG(self):
        #figure out how to do this directly from PIL
        pass

    def save(self):
        copy = self.surface
        copy.finish()







