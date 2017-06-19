import random as rd
import numpy as np
from matplotlib import pyplot as plt
from itertools import  *
from commons import *

global maxGridDistance
maxGridDistance = np.sqrt(2)

def generateResourceCoordinates(number_of_resources):
	return np.array([[float("%.2f" %rd.uniform(0,1)),float("%.2f" %rd.uniform(0,1))] for e in range(number_of_resources)])

def generateCoordinates(number_of_particles = 1, factor = 1):
	return np.array([[float("%.2f" %rd.uniform(0,1))*factor,float("%.2f" %rd.uniform(0,1))*factor] for e in range(number_of_particles)])

def generateVelocityVectors(number_of_particles = 1, factor = 0.5):
	return np.array([[float("%.2f" %rd.uniform(-0.5, 0.5))*factor,float("%.2f" %rd.uniform(-0.5, 0.5))*factor] for e in range(number_of_particles)])

def getNextTimestepCoordinates(coordinate_vectors, velocity_vectors):
	return _tackleOverTheGridCoords([_createMutation(list(np.array(c)+np.array(v))) for c,v in zip(coordinate_vectors, velocity_vectors)])

def remakeVelocityVectors(resource_locations_found, velocity_vectors):
	return [np.array([0,0]) if i in resource_locations_found.keys() else vel for i, vel in enumerate(velocity_vectors)]

def _createMutation(list_of_coordinates):
	if np.random.choice([True, False], p = [0.01,0.99]):
		return np.array(list_of_coordinates) + np.array([rd.uniform(-0.1,0.1),rd.uniform(-0.1,0.1)])
	else:
		return list_of_coordinates

def _tackleOverTheGridCoords(list_of_coords):
	return [[rd.uniform(0,1), rd.uniform(0,1)] if (not (0 < x < 1) or not(0 < y < 1)) else [x,y] for x,y in list_of_coords]

def searchForResourceAround(current_locations, resource_locations, iteration, radius = 1):
	found_locations_by_distance = {}
	for i, particle in enumerate(current_locations):
		for j, resource in enumerate(resource_locations):
			if distance(particle,resource) < radius:
				if i not in found_locations_by_distance:
					found_locations_by_distance[i] = []
					found_locations_by_distance[i].append([j, distance(particle, resource)])
					continue
				found_locations_by_distance[i].append([j, distance(particle, resource)])
	return getBestResources(iteration, found_locations_by_distance)

def getBestResources(iteration, found_locations_by_distance, signals_available = None):
	return { particle : getBestResourceForAParticle(iteration, resources) for particle, resources in found_locations_by_distance.iteritems()}

def getBestResourceForAParticle(iteration, location_of_resources):
	scores = { l : getScoreBySignals(iteration, dist) + getScoreByNumberOfIterationsSpent(iteration) for i, (l,dist) in enumerate(location_of_resources)}
	min_score = min(scores.values())
	return scores.keys()[scores.values().index(min_score)]

def getScoreByNumberOfIterationsSpent(iteration):
	return round(float(np.log(1+iteration)/np.log(2)), 2)

def getScoreBySignals(iteration, dist):
	return round(np.exp((maxGridDistance - dist)/maxGridDistance), 2)

def plotPoints(resource_locations, particle_locations):
	plt.scatter(zip(*resource_locations)[0],zip(*resource_locations)[1], c = 'r')
	plt.scatter(zip(*particle_locations)[0],zip(*particle_locations)[1], c = 'b')
	plt.xlim(0,1); plt.ylim(0,1)
	plt.show()
	
def gossip(max_gossip_distance, settlers, resource_locations, particle_locations):
	p_received_gossip = {}
	mod_settlers_by_resource = {}
	for k,v in settlers.iteritems():
		if v not in mod_settlers_by_resource:
			mod_settlers_by_resource[v] = []
			mod_settlers_by_resource[v].append(k)
			continue
		mod_settlers_by_resource[v].append(k)
	for i, (resource_index, particles_allocated) in mod_settlers_by_resource.iteritems():
		for j, (particle_index_dummy, current_location) in particle_locations.iteritems():
			if (particle_index != particle_index_dummy) and \
				distance(current_location, resource_locations[resource_allocated_to]):
				pass

def main(number_of_resources = 20, number_of_particles = 2):
	iterations = 1
	resource_vectors = generateResourceCoordinates(number_of_resources)
	coordinate_vectors = generateCoordinates(number_of_particles)
	velocity_vectors = generateVelocityVectors(number_of_particles)
	while iterations <= 10:
		# plotPoints(resource_vectors, coordinate_vectors)
		found_resource_locations = searchForResourceAround(coordinate_vectors, resource_vectors, iterations)
		velocity_vectors = remakeVelocityVectors(found_resource_locations, velocity_vectors)
		coordinate_vectors = getNextTimestepCoordinates(coordinate_vectors,velocity_vectors)
		settlers_locations = None
		iterations += 1

if __name__ == '__main__':
	main()