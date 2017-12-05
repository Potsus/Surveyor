## Where i'm at
as of right now the application is a set of loosely contained python files to download heightmap data from google maps and process it into a form i can lasercut

## where i want to be
Download data straight from NASA's SRTM project, or find a way to use the rasterized googlemaps data.

run that through gdal_contour to extract contours. this generates several shapefiles that i need to further process

### database
add these contours to the postgis database?
read them directly and create the vector files from there?
i probably want to add them to the database as it'll make reprojecting easier
add them to the db using 




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



## Google maps apis
Put your google maps api keys in a file called keys.py in an array called `gmapsApiKeys`