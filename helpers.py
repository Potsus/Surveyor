def importJson(file):
	import json
	from collections import OrderedDict
	with open(file) as json_data:
		return json.load(json_data, object_pairs_hook=OrderedDict)

def urlStyles(styles):
	stringifiedStyles = list(map(styleString, styles))
	string = '&'.join(stringifiedStyles)
	return string


def styleString(element):
	string = 'style=' + objectToString(element, ':', '|') 
	return string
		

def objectToString(object, pairSeperator, objectSeperator):
	#TODO clean this up, break it out into seperate lines
	return str(objectSeperator).join(['%s%s%s' % (key,pairSeperator, value) for (key, value) in object.items()])