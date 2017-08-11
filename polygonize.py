import cairocffi as cairo 




path = 'Locations/Mosquito Island/'

config = importYaml(path + 'config')

data = np.load(path+'heightmap.npy')

edgeDetect(data, 10)