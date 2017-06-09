import random as rd
import numpy as np
from matplotlib import pyplot as plt

global maxGridDistance
maxGridDistance = np.sqrt(2)

'''
class generateVectors():
	"""docstring for generateVectors"""
	def __init__(self, arg):
		super(generateVectors, self).__init__()
		self.arg = arg

class messageSearch(object):
	"""docstring for messageSearch"""
	def __init__(self, arg):
		super(messageSearch, self).__init__()
		self.arg = arg

class resourceUnderRadii(object):
	"""docstring for resourceUnderRadii"""
	def __init__(self, arg):
		super(resourceUnderRadii, self).__init__()
		self.arg = arg
'''

def generateResourceCoordinates(number_of_resources):
	'''
		Generates coordinates for number of resources
	'''
	return np.array([[float("%.2f" %rd.uniform(0,1)),float("%.2f" %rd.uniform(0,1))] for e in range(number_of_resources)])

def generateCoordinates(number_of_particles = 1, factor = 1):
	'''
		Generates candidate coordinates for depending on the number of particles
		factor scales the points generated on the grid. Should be less than or equal to 1
	'''
	return np.array([[float("%.2f" %rd.uniform(0,1))*factor,float("%.2f" %rd.uniform(0,1))*factor] for e in range(number_of_particles)])

def generateVelocityVectors(number_of_particles = 1, factor = 0.5):
	'''
		Generates random velocity equal to the number of particles
		factor is strictly less then 1 to keep up the particles in the system from moving over the grid
		though that is handled. 
	'''
	return np.array([[float("%.2f" %rd.uniform(-0.5, 0.5))*factor,float("%.2f" %rd.uniform(-0.5, 0.5))*factor] for e in range(number_of_particles)])

def getNextTimestepCoordinates(coordinate_vectors, velocity_vectors):
	'''
		Gets coordinates at the next time iterations. Nezt iteration is equivalent to one unit of time.
	'''
	return _tackleOverTheGridCoords([_createMutation(list(np.array(c)+np.array(v))) for c,v in zip(coordinate_vectors, velocity_vectors)])

def _createMutation(list_of_coordinates):
	'''
		Mutates some coordinates with a probability to jerk the system from some local minima
		Note : Applied for times where the coordinate values oscillate in locations
	'''
	if np.random.choice([True, False], p = [0.3,0.7]):
		return np.array(list_of_coordinates) + np.array([rd.uniform(-0.1,0.1),rd.uniform(-0.1,0.1)])
	else:
		return list_of_coordinates

def _tackleOverTheGridCoords(list_of_coords):
	'''
		Given a coordinate set, random value is inserted if atleast one of the coordinate in not valid
	'''
	return [[rd.uniform(0,1), rd.uniform(0,1)] if (not (0 < x < 1) or not(0 < y < 1)) else [x,y] for x,y in list_of_coords]

def searchForResourceAround(current_locations, resource_locations, iteration, radius = 0.005):
	'''
		Produces a dictionary with particle numbers as keys and the locations they had found in the radius specified
	'''
	found_locations = {}
	for i, particle in enumerate(current_locations):
		for j, resource in enumerate(resource_locations):
			if _distance(particle,resource) < radius:
				if i not in found_locations:
					found_locations[i] = []
					found_locations[i].append([j, _distance(particle, resource)])
					continue
				found_locations[i].append([j, _distance(particle, resource)])
	return getBestResources(iteration, found_locations)

def getBestResources(iteration, found_locations, signals_available = None):
	'''
		Getting best resource location based on scores given by two major functions
	'''
	return { particle : getBestResourceForAParticle(iteration, resources) for particle, resources in found_locations.iteritems()}

def getBestResourceForAParticle(iteration, location_of_resources):
	'''
		Get best resource for a particle
	'''
	scores = { l : getScoreBySignals(iteration, dist) + getScoreByNumberOfIterationsSpent(iteration) for i, (l,dist) in enumerate(location_of_resources)}
	min_score = min(scores.values())
	return scores.keys()[scores.values().index(min_score)]

def getScoreByNumberOfIterationsSpent(iteration):
	'''
		Returns a score based on the time a particle has spent without finding a resource
		Decreases as iterations increase over a log scale.
		Normalised to make it stay between 0 and 1.
	'''
	return round(float(np.log(1+iteration)/np.log(2)), 2)

def getScoreBySignals(iteration, dist):
	'''
		Gives the importance of signal that is reached if any.
	'''
	return round(np.exp((maxGridDistance - dist)/maxGridDistance), 2)

def remakeVelocityVectors(resource_locations_found, velocity_vectors):
	'''
		If resource found, velocity vectors of the particles will be made to zero
	'''
	return [np.array([0,0]) if i in resource_locations_found.keys() else vel for i, vel in enumerate(velocity_vectors)]

def _distance(point1, point2):
	'''
		Gives the euclidean distance
		Note : Replace with numpy's inbuilt function
	'''
	return reduce(lambda a,b : a+b ,list(map(lambda x : x**2, list(point1-point2))))

def plotPoints(resource_locations, particle_locations):
	'''
		Plot particle movement
	'''
	plt.scatter(zip(*resource_locations)[0],zip(*resource_locations)[1], c = 'r')
	plt.scatter(zip(*particle_locations)[0],zip(*particle_locations)[1], c = 'b')
	plt.xlim(0,1); plt.ylim(0,1)
	plt.show()
	
def main(number_of_resources = 10, number_of_particles = 20):
	iterations = 1
	resource_vectors = generateResourceCoordinates(number_of_resources)
	coordinate_vectors = generateCoordinates(number_of_particles)
	velocity_vectors = generateVelocityVectors(number_of_particles)
	while iterations <= 10:
		# plotPoints(resource_vectors, coordinate_vectors)
		found_resource_locations = searchForResourceAround(coordinate_vectors, resource_vectors, iterations)
		velocity_vectors = remakeVelocityVectors(found_resource_locations, velocity_vectors)
		coordinate_vectors = getNextTimestepCoordinates(coordinate_vectors,velocity_vectors)
		iterations += 1

if __name__ == '__main__':
	main()