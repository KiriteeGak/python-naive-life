import random as rd
from requests.models import *
from commons import *
import particleProperties

MAX_GRID_DISTANCE = np.sqrt(2)


class ConstValueGenerators:
    @staticmethod
    def generate_resource_coordinates(number_of_resources=1):
        """
            :argument
                number_of_resources (Int) : Number of resources to be generated on the map
            :returns
                (dict) : A dictionary with resource id and location
        """
        if type(number_of_resources) == int:
            return {_ + 1: [float("%.2f" % rd.uniform(0, 1)), float("%.2f" % rd.uniform(0, 1))] for _ in
                    range(number_of_resources)}
        else:
            raise TypeError("Number of resources should be of integer format")

    @staticmethod
    def generate_particle_coordinates(number_of_particles=1, factor=1):
        """
            :argument
                number_of_particles (Int) : Number of coordinates to be generated for the particles
                factor (float) : To scale down/up the coordinates as the original grid is a unit square plane
            :returns
                (dict) : Map of particle ids and coordinates
        """
        assert (type(number_of_particles) == int), "Format type of number of particles should be an integer"
        assert (0 < factor <= 1), "factor value should range between zero and one"
        assert (type(factor) in (float, int)), "factor value passed should be of type int"
        return {_ + 1: [float("%.2f" % rd.uniform(0, 1)) * factor, float("%.2f" % rd.uniform(0, 1)) * factor] for _ in
                range(number_of_particles)}

    @staticmethod
    def generate_velocity_vectors(number_of_particles=1, factor=0.5):
        """
            :argument
                number_of_particles (Int) : Number of velocity vectors to be generated for the particles
                factor (float) : To scale down/up the velocity vectors as the original grid is a unit square plane
            :returns
                (dict) : Map of particle ids and velocity vectors
        """
        return {_ + 1: [float("%.2f" % rd.uniform(-0.5, 0.5)) * factor, float("%.2f" % rd.uniform(-0.5, 0.5)) * factor]
                for _ in range(number_of_particles)}


class IterationValueGenerators:
    def get_next_positions(self, coordinate_vectors, velocity_vectors):
        """
            :argument
                coordinate_vectors (dict) : Map of particle ids and coordinates
                velocity_vectors (dict) : Map of particle ids and velocity vectors
            :returns
                (dict) : Map of particle ids and velocity for the next time step
        """
        return {_ + 1: mod_vel for _, mod_vel in enumerate(self._tackle_beyond_map_positions(
            [self._create_positional_mutation(list(np.array(c) + np.array(v))) for c, v in
             zip(coordinate_vectors.values(), velocity_vectors.values())]))}

    @staticmethod
    def remake_velocity_vectors(settlers, velocity_vectors):
        """
            :argument
                settlers (dict) : Map of particles that are settlers for a resource
                velocity_vectors (dict) : Map of particle ids with velocity vector
            :returns
                (dict) : Map of updated velocity vectors.
        """
        return {particle: (np.array([0, 0]) if particle in settlers else vel) for particle, vel in
                velocity_vectors.iteritems()}

    @staticmethod
    def _create_positional_mutation(coordinates, odds=None):
        """
            :argument
                coordinates (List) : List of coordinates for all the particles
                odds (List) : Mutation rate
            :returns
                (List) : Mutated coordinate list
        """
        if not odds:
            odds = [0.01, 0.99]
        assert (sum(odds) - 1.0 < 0.0001), "Sum of probabilities does not add up to one"
        if np.random.choice([True, False], p=odds):
            return np.array(coordinates) + np.array([rd.uniform(-0.1, 0.1), rd.uniform(-0.1, 0.1)])
        else:
            return coordinates

    @staticmethod
    def _tackle_beyond_map_positions(list_of_coords):
        """
            :argument :
                list_of_coords (List) : List of coordinates
            :returns
                (List) : List of coordinates making sure that are in the grid
        """
        return [[rd.uniform(0, 1), rd.uniform(0, 1)] if (not (0 < x < 1) or not (0 < y < 1)) else [x, y] for x, y in
                list_of_coords]


def _resource_search(settlers, current_locations, resource_locations, iteration, radius=0.02):
    """
        :argument
            settlers (dict) : Map of particle ids and the resources they got settled to, if any
            current_locations (dict) : Map of current locations of all the particles
            resource_locations (dict) : Map of resource locations dropped on the map
            iteration (int) :  Current generation the system is in
            radius (float) : The maximum distance to for a particle to find a resource around it
        :returns
            NEED SOME SEEING
    """
    resources_in_view = _view_based_search(current_locations, resource_locations, radius)
    resources_found_by_gossip = _get_resources_by_gossip(iteration, settlers, 0.05, resource_locations,
                                                         current_locations)
    settlers = _resource_particle_allocator(settlers, iteration, resources_in_view, resources_found_by_gossip)
    return settlers


def _view_based_search(current_locations, resource_locations, radius=0.2):
    """
        :argument
            current_locations (dict) : Map of current locations of all the particles
            resource_locations (dict) : Map of resource locations dropped on the map
            radius (float) : The maximum distance to for a particle to find a resource around it
        :returns
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


def _score_by_iterations(iteration, modifier=0.5):
    """
        :argument
            iteration (int) : Iteration the system currently in
            modifier (int) : modifies selection criteria
        :returns
            (float) : score based on iteration
    """
    return round(float(iteration / (modifier + iteration)), 5)


def _score_by_resource_particle_distance(dist):
    """
        :argument
            dist (Int) : distance between particle and resource
        :returns
            (float) : Score based on distance
    """
    return round(MAX_GRID_DISTANCE / (dist + MAX_GRID_DISTANCE), 5)


def _score_by_messages_received(msgs_received, factor=None):
    """
        :argument
            msgs_received : the number of particles the are settled to this
            factor (default : str; int): tune in for the probability of selection of source based on the msgs_received
        :returns
            (float) : Combined score for preference of resource
    """
    if factor:
        assert (type(factor) in [str, float, int]), "Factor should be of format int,float or by default a string"
    if not factor:
        return round(1 - (1 / np.exp(msgs_received)), 5)
    elif factor > 1:
        return round(1 - (1 / factor ** msgs_received), 5)
    else:
        raise ValueError("Factor should be greater than one for ideal selection")


def _get_resources_by_gossip(iteration, settlers, max_gossip_distance, resource_locations, particle_locations):
    """
        :argument
            iteration (Int) : Current generation the system is in
            max_gossip_distance (float) : A particle sends a gossip around a radius of max_gossip_distance
            settlers (dict) : Map with resource number and list of particles that are settled for this
            resource_locations (dict) : Map with resource number and the location of it on the map at curr. iteration
            particle_locations (dict) : Map with particle index and the current location of particles
        :returns
            ret (dict) : Map of particle as keys and resources (map) and their corresponding scores
    """

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
                    ret[particle][source] = {
                        'iteration_based_score': _score_by_iterations(iteration),
                        'distance_based_score': _score_by_resource_particle_distance(dist),
                        'gossip_based_score': _score_by_messages_received(msgs_received)
                    }
    return ret


def _resource_particle_allocator(settlers, iteration, view_radius_based, gossip_based):
    """
    :argument
        settlers : (dict) A map of settled particles to the resource it got settled to
        iteration: (int) The current iteration the system is in
        view_radius_based: (dict) Resources found based on the view radius
        gossip_based: (dict) Resources found on the basis of gossip radius
    :returns
        ret : (dict) Map of particle ids and resources they decided to settle to.
    """
    ret = {}
    for particle_id, resource_avail in view_radius_based.iteritems():
        if particle_id not in settlers:
            if len(gossip_based[particle_id]) == 0:
                ret[particle_id] = _selection_by_distribution(resource_avail, iteration, None, mode='distance_based')
            else:
                ret[particle_id] = _selection_by_distribution(resource_avail, iteration, gossip_based[particle_id],
                                                              mode='message_based')
    return ret


def _selection_by_distribution(resources_avail, iteration, resources_found_by_gossip, mode):
    """
        :argument
            resources_avail (dict) :
            iteration (int) : Current generation the system is in
            resources_found_by_gossip (dict) : Resources a particle has found with scores for each resource
            mode (string) : The mode in which the messaging system currently in
        :returns
            A random choice based on the distribution calculated by normalized scores
    """
    if mode == 'distance_based':
        unnormalized_scores_dict = {
            element_.keys()[0]: _score_by_resource_particle_distance(element_.values()[0]) * _score_by_iterations(
                iteration)
            for element_ in resources_avail}
    else:
        unnormalized_scores_dict = {
            res_id: score_dict['distance_based_score'] * score_dict['iteration_based_score'] * score_dict[
                'gossip_based_score']
            for res_id, score_dict in resources_found_by_gossip.iteritems()}
    normalised_scores = np.array(unnormalized_scores_dict.values()) / np.sum(unnormalized_scores_dict.values())
    return np.random.choice(unnormalized_scores_dict.keys(), p=normalised_scores)


def return_particle_properties(positions, velocities):
    """
    :argument
        positions: Positions given to initialise particles
        velocities: Velocities initialised for the particles
    :returns
        Map of particles to particle default attributes fer helping in describing the current state of particle
    """
    return {particle_id: particleProperties.ParticleProps(position, velocities[particle_id], [], [], False, False, True)
            for particle_id, position in positions.iteritems()}


def main(number_of_resources=4, number_of_particles=10):
    """Main function that runs simulations
        :argument
            number_of_resources: (int) Number of resources to be placed in the grid
            number_of_particles: (int) Number of particles to be generated on the grid
    """
    iterations = 1
    resource_vectors = ConstValueGenerators.generate_resource_coordinates(number_of_resources)
    coordinate_vectors = ConstValueGenerators.generate_particle_coordinates(number_of_particles)
    velocity_vectors = ConstValueGenerators.generate_velocity_vectors(number_of_particles)
    props = return_particle_properties(coordinate_vectors, velocity_vectors)
    settlers = {}
    while iterations <= 10:
        plot_points(resource_vectors.values(), coordinate_vectors.values())
        settlers = _resource_search(settlers, coordinate_vectors, resource_vectors, iterations)
        velocity_vectors = IterationValueGenerators.remake_velocity_vectors(settlers, velocity_vectors)
        coordinate_vectors = IterationValueGenerators().get_next_positions(coordinate_vectors, velocity_vectors)
        iterations += 1


if __name__ == '__main__':
    main()
