install mysql
install the rwquirements,txt using pip:
pip install -r requirements.txt

setup the mysql databases and users


tester = Location(name='Australia', north=-0.6911343999999999, south=-51.66332320000001, east=166.7429167, west=100.0911072)


psql -d surveydb -U surveyuser


install cairo
brew install cairo

brew install pkg-config

curl -L https://www.cairographics.org/releases/cairo-1.14.6.tar.xz -o cairo.tar.xz
tar -xf cairo.tar.xz && cd cairo-1.14.6
./configure --prefix=/usr/local --disable-dependency-tracking
make install


#for easier sed replacements in osx
brew install gnu-sed