#Save locations to the django model
from locations.models import Location
import yaml


#loads a yaml file with specified handle
def importYaml(filename):
    with open( (filename + '.yaml') ) as yaml_data:
        return yaml.safe_load(yaml_data)

locations = importYaml('locations/data')

for key, place in locations.iteritems():
    loc = Location(name = place['name'], north = place['bounds']['north'], south = place['bounds']['south'], east  = place['bounds']['east'], west  = place['bounds']['west'])
    loc.save()