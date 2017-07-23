class ParticleProps(object):
    """
        :argument
            position (List) : Gives the position of the particle at the current iteration
            velocity (List) : Gives velocity vector
            prev_positions (List) : Previous positions the particle has gone threw
            prev_velocities (List) : Previous velocities the particle has possessed in resp. particle position
            settled (Boolean) : Shows whether a particle has settled to a resource. Found a resource does not mean settled
            moving_to_resource : Shows whether the particle has currently and is headed in that direction
            searching : Particle still in search mode
        :returns
            ParticleProps class instance
    """

    def __init__(self, position, velocity, prev_positions, prev_velocities, settled, moving_to_resource, searching):
        self.position = position
        self.velocity = velocity
        self.prev_positions = prev_positions
        self.prev_velocities = prev_velocities
        self.settled = settled
        self.moving_to_resource = moving_to_resource
        self.searching = searching
