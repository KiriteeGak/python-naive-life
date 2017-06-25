import random as rd
import numpy as np
from matplotlib import pyplot as plt
from itertools import *
from commons import *

max_grid_distance = np.sqrt(2)


def generateResourceCoordinates(number_of_resources):
    return {_ + 1: [float("%.2f" % rd.uniform(0, 1)), float("%.2f" % rd.uniform(0, 1))] for _ in
            range(number_of_resources)}


def generateCoordinates(number_of_particles=1, factor=1):
    return {_ + 1: [float("%.2f" % rd.uniform(0, 1)) * factor, float("%.2f" % rd.uniform(0, 1)) * factor] for _ in
            range(number_of_particles)}


def generateVelocityVectors(number_of_particles=1, factor=0.5):
    return {_ + 1: [float("%.2f" % rd.uniform(-0.5, 0.5)) * factor, float("%.2f" % rd.uniform(-0.5, 0.5)) * factor] for
            _ in
            range(number_of_particles)}


def getNextTimeStepCoordinates(coordinate_vectors, velocity_vectors):
    return {_ + 1: mod_vel for _, mod_vel in enumerate(_tackleOverTheGridCoords(
        [_createMutation(list(np.array(c) + np.array(v))) for c, v in
         (coordinate_vectors.values(), velocity_vectors.values())]))}


def remakeVelocityVectors(settlers, velocity_vectors):
    return {particle: (np.array([0, 0]) if i in settlers else vel) for particle, vel in velocity_vectors.iteritems()}


def _createMutation(list_of_coordinates):
    if np.random.choice([True, False], p=[0.01, 0.99]):
        return np.array(list_of_coordinates) + np.array([rd.uniform(-0.1, 0.1), rd.uniform(-0.1, 0.1)])
    else:
        return list_of_coordinates


def _tackleOverTheGridCoords(list_of_coords):
    return [[rd.uniform(0, 1), rd.uniform(0, 1)] if (not (0 < x < 1) or not (0 < y < 1)) else [x, y] for x, y in
            list_of_coords]


def searchOrGetMessage(settlers, current_locations, resource_locations, iteration, radius=0.2):
    """
        Settlers should be already settled particles - particle index and resource it got settled to.
        resource locations is constant - As long as no food source is depleted and no new ones are dropped
    """
    all_resources_found_around = searchForResourceAround(current_locations, resource_locations, radius)
    resources_found_by_message_received = getResourcesByGossip(iteration, settlers, 0.4, all_resources_found_around,
                                                               resource_locations, current_locations)
    print "resources_found_by_message_received", resources_found_by_message_received
    exit()


def searchForResourceAround(current_locations, resource_locations, radius=0.2):
    found_locations_by_distance = {}
    for i, particle in current_locations.iteritems():
        for j, resource in resource_locations.iteritems():
            dist = distance(particle, resource)
            if dist < radius:
                if i not in found_locations_by_distance:
                    found_locations_by_distance[i] = []
                    found_locations_by_distance[i].append([j, dist])
                    continue
                found_locations_by_distance[i].append([j, dist])
    return found_locations_by_distance


def getBestResources(iteration, found_locations_by_distance):
    return {particle: getBestResourceForAParticle(iteration, resources) for particle, resources in
            found_locations_by_distance.iteritems()}


def getBestResourceForAParticle(iteration, location_of_resources):
    scores = {l: getScoreByDistance(dist) + getScoreByNumberOfIterationsSpent(iteration) for i, (l, dist) in
              enumerate(location_of_resources)}
    min_score = min(scores.values())
    return scores.keys()[scores.values().index(min_score)]


def getCombinedScore(iteration, dist, msgs_received, factor='exp'):
    return round(
        getScoreByNumberOfIterationsSpent(iteration) + getScoreByDistance(dist) + getScoreBySignals(msgs_received,
                                                                                                    factor), 3)


def getScoreByNumberOfIterationsSpent(iteration):
    return round(float(np.log(1 + iteration) / np.log(2)), 3)


def getScoreByDistance(dist):
    return round(np.exp((max_grid_distance - dist) / max_grid_distance), 3)


def getScoreBySignals(msgs_received, factor='exp'):
    if factor == 'exp':
        return round(1 - (1 / np.exp(msgs_received)), 4)
    elif factor > 1:
        return round(1 - (1 / factor ** msgs_received), 4)
    else:
        raise ValueError("Factor should be greater than one for ideal selection")


def getResourcesByGossip(iteration, settlers, max_gossip_distance, resources_around, resource_locations,
                         particle_locations):
    """
        Args:
            iteration (Int) : Current generation the system is in
            max_gossip_distance (float) : A particle sends a gossip around a radius of max_gossip_distance
            settlers (dict) : Map with resource number and list of particles that are settled for this
            resources_around : Particle within a gossip distance of a resource
            resource_locations : Map with resource number and the location of it on the map at curr. itertation
            particle_locations : Map with particle index and the current location of particles

        Returns:
            Note : SOME FUNCTIONS NEEDS TO BE ADDED
    """
    res_to_particles_settled_match = {}
    '''
        Gives {r_m : [ [p_n, d_n-r_m ] ]}
    '''
    for particle_id, source_id in settlers.iteritems():
        if source_id not in res_to_particles_settled_match:
            res_to_particles_settled_match[source_id] = []
            res_to_particles_settled_match[source_id].append(particle_id)
        else:
            res_to_particles_settled_match[source_id].append(particle_id)
    '''
        Should output a map of resources and msg received particles
    '''
    ret = {}
    for particle, loc in particle_locations.iteritems():
        ret[particle] = {}
        if particle not in settlers:
            for source, sour_loc in resource_locations.iteritems():
                dist = distance(loc, sour_loc)
                msgs_received = len(res_to_particles_settled_match.get(source, []))
                if dist <= max_gossip_distance:
                    ret[particle][source] = getCombinedScore(iteration, dist, msgs_received)
    return ret


def main(number_of_resources=5, number_of_particles=4):
    iterations = 1
    resource_vectors = generateResourceCoordinates(number_of_resources)
    coordinate_vectors = generateCoordinates(number_of_particles)
    velocity_vectors = generateVelocityVectors(number_of_particles)
    settlers = {}
    while iterations <= 10:
        plotPoints(resource_vectors.values(), coordinate_vectors.values())
        settlers = searchOrGetMessage(settlers, coordinate_vectors, resource_vectors, iterations)
        velocity_vectors = remakeVelocityVectors(settlers, velocity_vectors)
        coordinate_vectors = getNextTimeStepCoordinates(coordinate_vectors, velocity_vectors)
        iterations += 1


if __name__ == '__main__':
    main()
