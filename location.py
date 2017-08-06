


class location:
    locations = importYaml('locations')

    def __init__(self, name, north, south, east, west):
        self.name  = name
        self.north = north
        self.south = south
        self.east  = east
        self.west  = west

    def get(locChoice):


    def serialize(self):
        obj = {}
        obj['name']  = self.name
        obj['bounds']['north'] = self.north
        obj['bounds']['south'] = self.south
        obj['bounds']['east']  = self.east
        obj['bounds']['west']  = self.west
        return obj

    def deserialize(self, location):
        self.name  = location['name']
        self.north = location['bounds']['north']
        self.south = location['bounds']['south']
        self.east  = location['bounds']['east']
        self.west  = location['bounds']['west']


    def save(self):
        locations[self.choice] = self.serialize()
        saveYaml(locations, 'locations')
