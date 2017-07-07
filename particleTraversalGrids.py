import random as rd
from matplotlib import pyplot as plt
from itertools import *
from commons import *

max_grid_distance = np.sqrt(2)


class ConstValueGenerators():
    @staticmethod
    def generateResourceCoordinates(number_of_resources=1):
        """
            Args:
                number_of_resources (Int) : Number of resources to be generated on the map
            Returns:
                (dict) : A dictionary with resource id and location
        """
        if type(number_of_resources) == int:
            return {_ + 1: [float("%.2f" % rd.uniform(0, 1)), float("%.2f" % rd.uniform(0, 1))] for _ in
                    range(number_of_resources)}
        else:
            raise TypeError("Number of resources should be of integer format")

    @staticmethod
    def generateCoordinates(number_of_particles=1, factor=1):
        """
            Args:
                number_of_particles (Int) : Number of coordinates to be generated for the particles
                factor (float) : To scale down/up the coordinates as the original grid is a unit square plane
            Returns:
                (dict) : Map of particle ids and coordinates
        """
        assert (type(number_of_particles) == int), "Format type of number of particles should be an integer"
        assert (0 < factor <= 1), "factor value should range between zero and one"
        assert (type(factor) in (float, int)), "factor value passed should be of type int"
        return {_ + 1: [float("%.2f" % rd.uniform(0, 1)) * factor, float("%.2f" % rd.uniform(0, 1)) * factor] for _ in
                range(number_of_particles)}

    @staticmethod
    def generateVelocityVectors(number_of_particles=1, factor=0.5):
        """
            Args:
                number_of_particles (Int) : Number of velocity vectors to be generated for the particles
                factor (float) : To scale down/up the velocity vectors as the original grid is a unit square plane
            Returns:
                (dict) : Map of particle ids and velocity vectors
        """
        return {_ + 1: [float("%.2f" % rd.uniform(-0.5, 0.5)) * factor, float("%.2f" % rd.uniform(-0.5, 0.5)) * factor]
                for _ in range(number_of_particles)}


def getNextTimeStepCoordinates(coordinate_vectors, velocity_vectors):
    """
        Args:
            coordinate_vectors (dict) : Map of particle ids and coordinates
            velocity_vectors (dict) : Map of particle ids and velocity vectors
        Returns:
            (dict) : Map of particle ids and velocity for the next time step
    """
    return {_ + 1: mod_vel for _, mod_vel in enumerate(_tackleOverTheGridCoords(
        [_createMutation(list(np.array(c) + np.array(v))) for c, v in
         (coordinate_vectors.values(), velocity_vectors.values())]))}


def remakeVelocityVectors(settlers, velocity_vectors):
    """
        Args:
            settlers (dict) : Map of particles that are settlers for a resource
            velocity_vectors (dict) : Map of particle ids with velocity vector
        Returns:
            (dict) : Map of updated velocity vectors.
    """
    return {particle: (np.array([0, 0]) if particle in settlers else vel) for particle, vel in
            velocity_vectors.iteritems()}


def _createMutation(coordinates, odds=None):
    """
        Args:
            coordinates (List) : List of coordinates for all the particles
            odds (List) : Mutation rate
        Returns:
            (List) : Mutated coordinate list
    """
    if not odds:
        odds = [0.01, 0.99]
    assert (sum(odds) - 1 > 0.0001), "Sum of probabilities does not add up to one"
    if np.random.choice([True, False], p=odds):
        return np.array(coordinates) + np.array([rd.uniform(-0.1, 0.1), rd.uniform(-0.1, 0.1)])
    else:
        return coordinates


def _tackleOverTheGridCoords(list_of_coords):
    """
        Args :
            list_of_coords (List) : List of coordinates
        Returns:
            (List) : List of coordinates making sure that are in the grid
    """
    return [[rd.uniform(0, 1), rd.uniform(0, 1)] if (not (0 < x < 1) or not (0 < y < 1)) else [x, y] for x, y in
            list_of_coords]


def searchOrGetMessage(settlers, current_locations, resource_locations, iteration, radius=0.2):
    """
        Args:
            settlers (dict) : Map of particle ids and the resources they got settled to, if any
            current_locations (dict) : Map of current locations of all the particles
            resource_locations (dict) : Map of resource locations dropped on the map
            iteration (int) :  Current generation the system is in
            radius (float) : The maximum distance to for a particle to find a resource around it
        Returns:
            NEED SOME SEEING
    """
    resources_in_view = searchForResourceAround(current_locations, resource_locations, radius)
    resources_found_by_gossip = getResourcesByGossip(iteration, settlers, 0.4, resource_locations,
                                                     current_locations)
    print settleParticlesDown(settlers, iteration, resources_in_view, resources_found_by_gossip)
    exit()


def searchForResourceAround(current_locations, resource_locations, radius=0.2):
    """
        Args : 
            current_locations (dict) : Map of current locations of all the particles
            resource_locations (dict) : Map of resource locations dropped on the map
            radius (float) : The maximum distance to for a particle to find a resource around it
        Returns:
            (dict) : Map of particle ids and resources it has found around
    """
    found_locations_by_distance = {}
    for i, particle in current_locations.iteritems():
        for j, resource in resource_locations.iteritems():
            dist = distance(particle, resource)
            if dist < radius:
                if i not in found_locations_by_distance:
                    found_locations_by_distance[i] = []
                    found_locations_by_distance[i].append({j: dist})
                    continue
                found_locations_by_distance[i].append({j: dist})
    return found_locations_by_distance


def getCombinedScore(iteration, dist, msgs_received, factor='exp'):
    """
        Args:
            iteration (Int) : Iteration the system currently in
            dist (Int) : distance between particle and resource
            msgs_received : the number of particles the are settled to this
            factor (default : str; int): tune in for the probability of selection of source based on the msgs_received
        Returns:
            (float) : Combined score for preference of resource
    """
    return round(
        getScoreByIterationsSpent(iteration) / (getScoreByDistance(dist) + getScoreBySignals(msgs_received,
                                                                                             factor)), 3)


def getScoreByIterationsSpent(iteration, modifier=0.5):
    """
        Args:
            iteration (int) : Iteration the system currently in
            modifier (int) : modifies selection criteria
        Returns:
            (float) : score based on iteration
    """
    return round(float(iteration / (modifier + iteration)), 3)


def getScoreByDistance(dist):
    """
        Args:
            dist (Int) : distance between particle and resource
        Returns:
            (float) : Score based on distance
    """
    return round(max_grid_distance / (dist + max_grid_distance), 3)


def getScoreBySignals(msgs_received, factor='exp'):
    """
        Args:
            msgs_received : the number of particles the are settled to this
            factor (default : str; int): tune in for the probability of selection of source based on the msgs_received
        Returns:
            (float) : Combined score for preference of resource
    """
    assert (type(factor) in [str, float, int]), "Factor should be of format int,float or by default a string"
    if factor == 'exp':
        return round(1 - (1 / np.exp(msgs_received)), 4)
    elif factor > 1:
        return round(1 - (1 / factor ** msgs_received), 4)
    else:
        raise ValueError("Factor should be greater than one for ideal selection")


def getResourcesByGossip(iteration, settlers, max_gossip_distance, resource_locations, particle_locations):
    """
        Args:
            iteration (Int) : Current generation the system is in
            max_gossip_distance (float) : A particle sends a gossip around a radius of max_gossip_distance
            settlers (dict) : Map with resource number and list of particles that are settled for this
            resource_locations : Map with resource number and the location of it on the map at curr. iteration
            particle_locations : Map with particle index and the current location of particles

        Returns:
            Note : SOME FUNCTIONS NEEDS TO BE ADDED
    """

    # should return source map[(id -> [particle_ids])

    res_to_particles_settled_match = {}
    for particle_id, source_id in settlers.iteritems():
        if source_id not in res_to_particles_settled_match:
            res_to_particles_settled_match[source_id] = []
        res_to_particles_settled_match[source_id].append(particle_id)
    ret = {}
    for particle, loc in particle_locations.iteritems():
        ret[particle] = {}
        if particle not in settlers:
            for source, sour_loc in resource_locations.iteritems():
                dist = distance(loc, sour_loc)
                msgs_received = len(res_to_particles_settled_match.get(source, []))
                if msgs_received != 0 and dist <= max_gossip_distance:
                    ret[particle][source] = getCombinedScore(iteration, dist, msgs_received)
                    ret[particle][source] = {
                        'iteration_based_score': getScoreByIterationsSpent(iteration),
                        'distance_based_score': getScoreByDistance(dist),
                        'gossip_based_score': getScoreBySignals(msgs_received)
                    }
    return ret


def settleParticlesDown(settlers, iteration, view_radius_based, gossip_based):
    ret = {}
    for particle_id, resource_avail in view_radius_based.iteritems():
        if particle_id not in settlers:
            if len(gossip_based[particle_id]) == 0:
                ret[particle_id] = getProbableSelections(resource_avail, iteration, mode='distance_based')
            else:
                ret[particle_id] = getProbableSelections(resources_avail, iteration, mode='message_based')
    return ret


def getProbableSelections(resources_avail, iteration, mode):
    """
        resources_avail (dict) : 
        iteration (int) : 
        mode (string) : 
    """
    if mode == 'distance_based':
        unnormalized_scores = np.array(
            [getScoreByDistance(e.values()[0]) * getScoreByIterationsSpent(iteration) for e in resources_avail],
            dtype=float)
    elif mode == 'message_based':
        unnormalized_scores = [e for e in resources_avail]
    normalised_scores = unnormalized_scores / np.sum(unnormalized_scores)
    assert (sum(normalised_scores) - 1 <= 0), "Check the normalising function"
    return np.random.choice([e.keys()[0] for e in resources_avail], p=normalised_scores)


def main(number_of_resources=4, number_of_particles=10):
    iterations = 1
    resource_vectors = ConstValueGenerators.generateResourceCoordinates(number_of_resources)
    coordinate_vectors = ConstValueGenerators.generateCoordinates(number_of_particles)
    velocity_vectors = ConstValueGenerators.generateVelocityVectors(number_of_particles)
    settlers = {}
    while iterations <= 10:
        # plotPoints(resource_vectors.values(), coordinate_vectors.values())
        settlers = searchOrGetMessage(settlers, coordinate_vectors, resource_vectors, iterations)
        velocity_vectors = remakeVelocityVectors(settlers, velocity_vectors)
        coordinate_vectors = getNextTimeStepCoordinates(coordinate_vectors, velocity_vectors)
        iterations += 1


if __name__ == '__main__':
    main()
