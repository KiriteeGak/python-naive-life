import random as rd
import numpy as np
from matplotlib import pyplot as plt
from itertools import *
from commons import *

global maxGridDistance
maxGridDistance = np.sqrt(2)


def generateResourceCoordinates(number_of_resources):
    return np.array(
        [[float("%.2f" % rd.uniform(0, 1)), float("%.2f" % rd.uniform(0, 1))] for e in range(number_of_resources)])


def generateCoordinates(number_of_particles=1, factor=1):
    return np.array([[float("%.2f" % rd.uniform(0, 1)) * factor, float("%.2f" % rd.uniform(0, 1)) * factor] for e in
                     range(number_of_particles)])


def generateVelocityVectors(number_of_particles=1, factor=0.5):
    return np.array(
        [[float("%.2f" % rd.uniform(-0.5, 0.5)) * factor, float("%.2f" % rd.uniform(-0.5, 0.5)) * factor] for e in
         range(number_of_particles)])


def getNextTimestepCoordinates(coordinate_vectors, velocity_vectors):
    return _tackleOverTheGridCoords(
        [_createMutation(list(np.array(c) + np.array(v))) for c, v in zip(coordinate_vectors, velocity_vectors)])


def remakeVelocityVectors(resource_locations_found, velocity_vectors):
    return [np.array([0, 0]) if i in resource_locations_found.keys() else vel for i, vel in enumerate(velocity_vectors)]


def _createMutation(list_of_coordinates):
    if np.random.choice([True, False], p=[0.01, 0.99]):
        return np.array(list_of_coordinates) + np.array([rd.uniform(-0.1, 0.1), rd.uniform(-0.1, 0.1)])
    else:
        return list_of_coordinates


def _tackleOverTheGridCoords(list_of_coords):
    return [[rd.uniform(0, 1), rd.uniform(0, 1)] if (not (0 < x < 1) or not (0 < y < 1)) else [x, y] for x, y in
            list_of_coords]


def searchOrGetMessage(settlers, current_locations, resource_locations, iteration, particle_locations, radius=0.2):
    '''
        Settlers should be already settled particles - particle index and resource it got settled to.
        resource locations is constant - As long as no food source is depleted and no new ones are dropped
    '''
    (allresources_found_around, resources_found_by_distance_alone) = searchForResourceAround(current_locations, \
                                                                                             resource_locations,
                                                                                             iteration, radius)
    resources_found_by_message_received = getResourcesByGossip(iteration, settlers, 0.4, allresources_found_around,
                                                               resource_locations, particle_locations)
    # print "resources_found_by_message_received", resources_found_by_message_received
    exit()


def searchForResourceAround(current_locations, resource_locations, iteration, radius=0.2):
    found_locations_by_distance = {}
    for i, particle in enumerate(current_locations):
        for j, resource in enumerate(resource_locations):
            if distance(particle, resource) < radius:
                if i not in found_locations_by_distance:
                    found_locations_by_distance[i] = []
                    found_locations_by_distance[i].append([j, distance(particle, resource)])
                    continue
                found_locations_by_distance[i].append([j, distance(particle, resource)])
    return found_locations_by_distance, getBestResources(iteration, found_locations_by_distance)


def getBestResources(iteration, found_locations_by_distance, signals_available=None):
    return {particle: getBestResourceForAParticle(iteration, resources) for particle, resources in
            found_locations_by_distance.iteritems()}


def getBestResourceForAParticle(iteration, location_of_resources):
    scores = {l: getScoreBySignals(iteration, dist) + getScoreByNumberOfIterationsSpent(iteration) for i, (l, dist) in
              enumerate(location_of_resources)}
    min_score = min(scores.values())
    return scores.keys()[scores.values().index(min_score)]


def getScoreByNumberOfIterationsSpent(iteration):
    return round(float(np.log(1 + iteration) / np.log(2)), 2)


def getScoreBySignals(iteration, dist):
    return round(np.exp((maxGridDistance - dist) / maxGridDistance), 2)


def getResourcesByGossip(iteration, settlers, max_gossip_distance, resources_around, resource_locations,
                         particle_locations):
    '''
        Args:
            max_gossip_distance (float) : A particle sends a gossip around a radius of max_gossip_distance
            settlers (dict) : Map with resource number and list of particles that are settled for this
            resources_around : Particle within a gossip distance of a resource
            resource_locations : Map with resource number and the location of it on the map at curr. itertation
            particle_locations : Map with particle index and the current location of particles

        Returns:
            Note : SOME FUNCTIONS NEEDS TO BE ADDED
    '''
    p_received_gossip = {}
    mod_settlers_by_resource = {}
    '''
        Gives {r_m : [ [p_n, d_n-r_m ] ]}
    '''
    for particle_id, v in resources_around.iteritems():
        for i, [source_id, distance] in enumerate(v):
            if source_id not in mod_settlers_by_resource:
                mod_settlers_by_resource[source_id] = []
                mod_settlers_by_resource[source_id].append([particle_id, distance])
            else:
                mod_settlers_by_resource[source_id].append([particle_id, distance])
    '''
        Should output a map of resources and msg received particles
    '''
    ret = {}
    for particle_id, vals in resources_around.iteritems():
        if particle_id not in settlers.keys():
            ret[particle_id] = {}
            for i, (res_id, distance) in enumerate(vals):
                priority_val = getScoreByNumberOfIterationsSpent(iteration) + getScoreBySignals(iteration, distance)
                ret[particle_id][res_id] = priority_val
    print ret
    exit()


def main(number_of_resources=10, number_of_particles=2):
    iterations = 1
    resource_vectors = generateResourceCoordinates(number_of_resources)
    coordinate_vectors = generateCoordinates(number_of_particles)
    velocity_vectors = generateVelocityVectors(number_of_particles)
    found_resource_locations = {}
    settlers = {}
    while iterations <= 10:
        # plotPoints(resource_vectors, coordinate_vectors)
        found_resource_locations = searchOrGetMessage(settlers, coordinate_vectors, resource_vectors, iterations,
                                                      found_resource_locations)
        velocity_vectors = remakeVelocityVectors(found_resource_locations, velocity_vectors)
        coordinate_vectors = getNextTimestepCoordinates(coordinate_vectors, velocity_vectors)
        iterations += 1


if __name__ == '__main__':
    main()
