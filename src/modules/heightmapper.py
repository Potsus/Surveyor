class heightmapper:

    def scan(self):
        if self.eGrid != []:
            return False
        elif self.loadArea():
            return True
        else:
            choice = raw_input('fetching grid sized %s x %s is this ok? (y/n) ' % (self.xResolution, self.yResolution))
            if choice != 'y':
                #quit if we don't want to continue
                exit()

            #get data from google
            for y in range (0, self.yResolution):

                sampleLat = self.north - (self.tick * y)
                print 'fetching gridline %s of %s' % (str(y), self.yResolution)
                row = self.getRow(sampleLat)
                self.eGrid.append(row)
                self.cleanGrid.append(cleanRow(row))
                #print(' complete')

            self.saveCollectedData()


    def getRow(self, lat):
        x   = 0
        row = []
        while(x < self.xResolution):
            #make sure you don't go past elevation resolution
            samplesToRequest = config['max_samples_per_request']
            if(x + samplesToRequest > self.xResolution):
                samplesToRequest = self.xResolution - x

            row.extend(self.requestLineFragment(lat, samplesToRequest, x))
            #print x,
            x += samplesToRequest
        return row


    
    def requestLineFragment(self, lineLat, samples, start):
        #if we've run out of keys return junk data
        if (self.keyNum >= len(config['keys'])):
            return makeJunkData(samples)

        lineLng = self.east - (self.tick * start)

        queryString  = "%s?path=%s,%s|%s,%s&samples=%s&key=%s" % (config['urls']['elevation'], lineLat, lineLng, lineLat, lineLng - (self.tick * (samples -1)), samples, config['keys'][self.keyNum])
        response     = requests.get(queryString)
        
        try:
            responseData = json.loads(response.content)
        except(e):
            print(e.message + " filling with junk")
            return makeJunkData(samples)

        if responseData['status'] != 'OK':
            print('response error: %s' % responseData['status'])
            self.useNextKey()
            return self.requestLineFragment(lineLat, samples, start)

        return responseData['results']