import random as rd
import numpy as np

def generateResourceCoordinates(number_of_resources):
	return np.array([[float("%.2f" %rd.random()),float("%.2f" %rd.random())]for e in range(number_of_resources)])

def generateCoordinates(number_of_particles = 1, factor = 1):
	return np.array([[float("%.2f" %rd.random())*factor,float("%.2f" %rd.random())*factor] for e in range(number_of_particles)])

def generateVelocityVectors(number_of_particles = 1, factor = 0.1):
	return np.array([[float("%.2f" %rd.random())*factor,float("%.2f" %rd.random())*factor] for e in range(number_of_particles)])

def getNextTimestepCoordinates(coordinate_vectors, velocity_vectors):
	return [np.array(c)+np.array(v) if for c,v in zip(coordinate_vectors, velocity_vectors)]

def searchForResourceAround(current_locations, resource_locations, radius = 0.05):
	found_locations = {}
	for i, particle in enumerate(current_locations):
		for j, resource in enumerate(resource_locations):
			if distance(particle,resource) < radius:
				if i not in found_locations:
					found_locations[i] = []
					found_locations[i].append([j, distance(particle, resource)])
					continue
				found_locations[i].append([j, distance(particle, resource)])
	return getBestResources(found_locations)

def getBestResources(found_locations):
	return { k : list(zip(*v)[0])[list(zip(*v)[1]).index(max(zip(*v)[1]))] for k,v in found_locations.iteritems()}

def remakeVelocityVectors(resource_locations_found, velocity_vectors):
	return [np.array([0,0]) if i in resource_locations_found.keys() else vel for i, vel in enumerate(velocity_vectors)]

def distance(point1, point2):
	return reduce(lambda a,b : a+b ,list(map(lambda x : x**2, list(point1-point2))))

def messageDampner(radius, drop_rate):
	pass

def sendMessage(radius):
	pass

def objectiveFunction():
	return True

def main(covergence = True, iterations = 0):
	resource_vectors = generateResourceCoordinates(1)
	coordinate_vectors = generateCoordinates(2)
	velocity_vectors = generateVelocityVectors(2)
	while objectiveFunction() and iterations < 20:
		found_resource_locations = searchForResourceAround(coordinate_vectors, resource_vectors)
		velocity_vectors = remakeVelocityVectors(found_resource_locations, velocity_vectors)
		coordinate_vectors = getNextTimestepCoordinates(coordinate_vectors,velocity_vectors)
		iterations += 1
		print coordinate_vectors,"\n"
	# curr_velocity = coordinate_vectors

if __name__ == '__main__':
	main()