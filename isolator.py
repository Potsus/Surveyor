from helpers import *
from mapper import Mapper
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

print('starting isolator')

location = getLocation(locChoice='vi')

mapper = Mapper(location['name'], location['bounds']['north'], location['bounds']['south'], location['bounds']['east'], location['bounds']['west'])
#getValue('what zoom level would you like?', testZoom)
mapper.setZoom(14)
mapper.setStyle(styles['nolables'])
mapper.fetchArea()
#mapper.betterFetch()

