from Tkinter import *
import os.path
from PIL import Image, ImageTk
import os
from helpers import *

locations = importYaml('locations')


#present location options
locChoice = raw_input('pick a location to scan ' + str(locations.keys()) + ' :')
#locChoice = 'vi'


#load selection data
if keyExists(locations, locChoice):
    location = locations[locChoice]
else: 
    exit()

#----------------------------------------------------------------------

class MainWindow():

    #----------------

    def __init__(self, main):

        path = 'slices/%s/' % location['name']

        #get the dimensions of the images we're working with
        self.files = filter( lambda f: not f.startswith('.'), os.listdir(path))
        #self.files = self.files.sort()
        sizer = Image.open(path + self.files[0])
        width, height = sizer.size

        # canvas for image
        self.canvas = Canvas(main, width=width, height=height)
        self.canvas.grid(row=0, column=0)


        # images
        self.my_images = []
        for filename in self.files:
            image = Image.open(path + filename)
            #image = image.resize((width/2, height/2), Image.ANTIALIAS)
            image = ImageTk.PhotoImage(image)
            self.my_images.append(image)

        self.my_image_number = 0

        # set first image on canvas
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor = NW, image = self.my_images[0])

        # button to change image
        self.slider = Scale(master=None, from_=0, to=len(os.listdir(path))-1, command=self.onSlider)
        self.slider.grid(row=0, column=1)

    #----------------

    def onSlider(self, value):

        print(value)
        # next image
        self.my_image_number = int(value)

        # change image
        self.canvas.itemconfig(self.image_on_canvas, image = self.my_images[self.my_image_number])

#----------------------------------------------------------------------

root = Tk()
MainWindow(root)
root.mainloop()
