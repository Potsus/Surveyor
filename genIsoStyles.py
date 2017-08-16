#when run will generate styles to isolate the geometry of all features google allows the styling of
#relies on a list of features, a style to 


from helpers import *
features = importYaml('features')
styles   = importYaml('styles')

blankStyle = dict()
  blankStyle['element'] = 'all'
  blankStyle['feature'] = 'all'
  blankStyle['visibility'] = 'off'

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
        water = dict()
        water['feature']    = 'water'
        water['element']    = 'geometry'
        water['color']      = '0x000000'
        water['visibility'] = 'on'
        out.append(style)

    print(out)
    return out

for feature in features:
    print(feature)
    styles[feature] = isolateFeature(feature)
    print('')

saveYaml(styles, 'styles')