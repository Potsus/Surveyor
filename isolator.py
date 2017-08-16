from helpers import *
from mapper import mapper
config = importYaml('config')
features = importYaml('features')
styles = importYaml('styles')



def testZoom(zoom):
    if canCastToInt(zoom) == False:
        print 'please give an int'
        return False
    mapper.setZoom(int(zoom))
    print 'is this ok?'
    return yn()

#import logging
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
print('starting isolator')

location = getLocation()

mapper = mapper(location['name'], location['bounds']['north'], location['bounds']['south'], location['bounds']['east'], location['bounds']['west'])
getValue('what zoom level would you like?', testZoom)

#mapper.setStyle()
mapper.fetchArea()

