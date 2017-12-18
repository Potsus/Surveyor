## Where i'm at
as of right now the first pass on the application is a set of loosely contained python files to download heightmap data from google maps and process it into a form i can lasercut

## Second pass is starting now
`downloadSRTM.py` will fetch the relevant SRTM data and clip it to the specified bounds.
it can also generate contours into another folder
also has a function to import those contours to a postgis database
`contour.py` will take the shapefiles generated by gdal_contour and generate a pdf so you can see what's going on.

### TODO:
Write some instal scripts to properly install GDAL, CAIRO

i need to abstract out the functionality to more than the one demo i did so multiple locations. duh

ignore single points and straight lines so check the number of points in a line and ignore lines where the bbox doesn't change on both dimensions

i tried splitting the different shapes out based on their `shapeType` attribute but they all register as type `3` which is a line so that's useless

clip the data to ignore patches of ocean or min at 0
`GDAL_Contour` has a `-3d` flag that will include height data with every point I could use that to order the layers by including a preprocessing step to strip out the height data and determine a height for each layer
i need to do that so i can burn location holes into the previous layer

http://www.gdal.org/gdal_contour.html
there are a couple of interesting flags like `-off` to set an offset to start from and `-fi` to get specific levels

the contour file also contains some useful information including 

use `rasterio` to apply the high detail shorline data as a mask and delete everything not in the mask before doing contours

convert my google maps data to a geo tiff with csvtotiff.py


## where i want to be
Download data straight from NASA's SRTM project, or find a way to use the rasterized googlemaps data.

run that through gdal_contour to extract contours. this generates several shapefiles that i need to further process

### database
add these contours to the postgis database?
read them directly and create the vector files from there?
i probably want to add them to the database as it'll make reprojecting easier
add them to the db using `shp2pgsql`




Write those contours to a vector file the lasercutter can read





---

install mysql
install the rwquirements,txt using pip:
pip install -r requirements.txt

setup the mysql databases and users


tester = Location(name='Australia', north=-0.6911343999999999, south=-51.66332320000001, east=166.7429167, west=100.0911072)


psql -d surveydb -U surveyuser


## cairo
install cairo
`brew install cairo`

`brew install pkg-config`

```curl -L https://www.cairographics.org/releases/cairo-1.14.6.tar.xz -o cairo.tar.xz
tar -xf cairo.tar.xz && cd cairo-1.14.6
./configure --prefix=/usr/local --disable-dependency-tracking
make install
```

probably need cairocffi for python bindings

## install gdal
Installing the python bindings seems to be a pain to do from pip


OSX: http://www.kyngchaos.com/software:frameworks
go there and install gdal 2.1 complete


## SRTM 
```sudo apt install python-pip gdal-bin postgis
sudo pip install elevation```

## for easier sed replacements in osx
brew install gnu-sed


install the java development kit, or jdk
then
`java -jar heightmap2stl.jar <path to image> <height of model> <height of base>`

## GSHHS or Vector shorline data

We probably want to use the full resolution vectors for land, islands, lakes, ponds and antarctica
so we'll be using the **f** data and to start just the **L1** files but ultimately all the different Ls. I'm not sure how to access the river and political border data yet

The geography data come in five resolutions, 
the files for which are in the folder with the corresponding letter:
    **f**ull resolution: Original (full) data resolution.
    **h**igh resolution: About 80 % reduction in size and quality.
    **i**ntermediate resolution: Another ~80 % reduction.
    **l**ow resolution: Another ~80 % reduction.
    **c**rude resolution: Another ~80 % reduction.


Unlike the shoreline polygons at all resolutions, the lower resolution rivers are not guaranteed to be free of intersections.
Shorelines are furthermore organized into 6 hierarchical levels:
    L1: boundary between land and ocean, except Antarctica.
    L2: boundary between lake and land.
    L3: boundary between island-in-lake and lake.
    L4: boundary between pond-in-island and island.
    L5: boundary between Antarctica ice and ocean.
    L6: boundary between Antarctica grounding-line and ocean.

Rivers are organized into 10 classification levels:
    L0: Double-lined rivers (river-lakes).
    L1: Permanent major rivers.
    L2: Additional major rivers.
    L3: Additional rivers.
    L4: Minor rivers.
    L5: Intermittent rivers - major.
    L6: Intermittent rivers - additional.
    L7: Intermittent rivers - minor.
    L8: Major canals.
    L9: Minor canals.
    L10: Irrigation canals.

Finally, borders are organized into three levels:
    L1: National boundaries.
    L2: State boundaries within the Americas.
    L3: Marine boundaries.


## Google maps apis
Put your google maps api keys in a file called keys.py in an array called `gmapsApiKeys`