"""Everything related with the simulation of a node."""


class Node:
    """Defines attributes and methods needed in both sink and sensing nodes."""

    def __init__(self, address, name=None):
        self.address = address
        if name:
            self.name = name
        else:
            self.name = str(address)
        self.neighbours = set()

    def find_neighbours(self):
        """Discovers the neighbour nodes."""
        pass

    def __repr__(self):
        return '{0}, {1}'.format(self.address, self.name)

    def __str__(self):
        return '{0}, {1}'.format(self.address, self.name)


class SensingNode(Node):
    """Defines attributes and methods of a regular sensing (not sink) node."""

    def __init__(self, address, name=None):
        super(SensingNode, self).__init__(address, name)

    def get_next_hop_node(self):
        """Returns the node to route data."""
        pass


class SinkNode(Node):
    """Defines attributes and methods specific for a sink node."""

    def __init__(self, address, name=None):
        super(SinkNode, self).__init__(address, name)
        pass
