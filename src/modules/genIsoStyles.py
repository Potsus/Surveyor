#when run will generate styles to isolate the geometry of all features google allows the styling of
#relies on a list of features, a style to 


from helpers import *
features = importYaml('features')
styles   = importYaml('styles')

blankStyle = dict()
blankStyle['element']    = 'all'
blankStyle['feature']    = 'all'
blankStyle['visibility'] = 'off'

showWater = dict()
showWater['feature']    = 'water'
showWater['element']    = 'geometry'
showWater['color']      = '0x000000'
showWater['visibility'] = 'on'

showLand = dict()
showLand['feature']    = 'landscape'
showLand['element']    = 'geometry'
showLand['color']      = '0x000000'
showLand['visibility'] = 'on'

def isolateFeature(feature):
    out = []
    out.append(blankStyle) 

    style = dict()
    style['feature']    = feature
    style['element']    = 'geometry'
    style['color']      = '0xffffff'
    style['visibility'] = 'on'
    out.append(style)

    if 'landscape' in feature:
        out.append(showWater)

    if 'water' in feature:
        out.append(showLand)

    print(out)
    return out

for feature in features:
    print(feature)
    styles[feature] = isolateFeature(feature)
    print('')

saveYaml(styles, 'styles')