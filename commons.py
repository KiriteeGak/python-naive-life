def distance(point1, point2):
	return round(reduce(lambda a,b : a+b ,list(map(lambda x : x**2, list(point1-point2)))),3)

def plotPoints(resource_locations, particle_locations):
	plt.scatter(zip(*resource_locations)[0],zip(*resource_locations)[1], c = 'r')
	plt.scatter(zip(*particle_locations)[0],zip(*particle_locations)[1], c = 'b')
	plt.xlim(0,1); plt.ylim(0,1)
	plt.show()