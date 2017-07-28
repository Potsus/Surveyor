





def ticksToResolution(a,b):
    #no longer needed because resolution doesn't have to devide into even numbers
    #pixels should be sampled in the center of their pixel
    #this will almost never devide evenly for the last line segment in a row
    #but the deviance is practically nothing for most purposes
    #return roundToEven(abs(a - b) / TICK)
    return int(math.ceil(abs(a - b) / TICK))

def useNextKey():
    global keyNum
    keyNum += 1

def makeJunkData(samples):
    junkData = []
    for i in range(0, samples):
        junkData.append(junkSample)
    return junkData

def getFragmentSamples(desiredSamples):
    if desiredSamples > config['max_samples_per_request']:
        return getFragmentSamples(desiredSamples/2)
    return int(math.floor(desiredSamples))

def requestLineFragment(lineLat, samples, start):
    #if we've run out of keys return junk data
    if (keyNum >= len(config['keys'])):
        return makeJunkData(samples)

    lineLng = location['bounds']['east'] - (TICK * start)

    queryString  = "%s?path=%s,%s|%s,%s&samples=%s&key=%s" % (config['urls']['elevation'], lineLat, lineLng, lineLat, lineLng - (TICK * (samples -1)), samples, config['keys'][keyNum])
    response     = requests.get(queryString)
    responseData = json.loads(response.content)
    if responseData['status'] != 'OK':
        logging.debug('response error: %s' % responseData['status'])
        useNextKey()
        return requestLineFragment(lineLat, samples, start)

    return responseData['results']



def getLat(point):
    return point['location']['lng']

def getRow(lat):
    x   = 0
    row = []
    while(x < xResolution):
        #make sure you don't go past elevation resolution
        if(x + samplesToRequest > xResolution):
            samplesToRequest = xResolution - x
        else:
            samplesToRequest = config['max_samples_per_request']

        row.extend(requestLineFragment(lat, samplesToRequest, x))
        print x,
        x += samplesToRequest
    return row

def clipLowerBound(dataArray, lowerBound):
    return np.clip(dataArray, lowerBound, dataArray.max())

def saveAsImage(data, filename):
    imageData = (255*(data - np.max(data))/-np.ptp(data)).astype(int)

    #generate heightmap
    heightMap = Image.fromarray(imageData.astype('uint8'))
    heightMap = PIL.ImageOps.invert(heightMap)
    heightMap = heightMap.transpose(Image.FLIP_LEFT_RIGHT)
    heightMap.save(filename + '.png')

def makeSlice(data, lower, upper):
    data = np.clip(data, lower, upper)
    suffix = (' %s-%s' % (upper, lower))
    print('generating image with bounds %s' % suffix)
    saveAsImage(data, 'slices/' + filename + suffix)

def generateCuts(data, min, numLayers):
    layerHeight = (data.max() - min) / numLayers

    for i in range(1, numLayers+1):
        upper = (data.max() - (layerHeight * (i-1)))
        lower = (data.max() - (layerHeight * i))
        
        makeSlice(data, lower, upper)

def nameLookup(name, locations):
    for location in locations.iteritems():
        if location[1]['name'] == name:
            return location
    return False


