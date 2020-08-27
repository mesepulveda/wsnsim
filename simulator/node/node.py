"""Everything related with the simulation of a node."""


class _Node:
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


class SensingNode(_Node):
    """Defines attributes and methods of a regular sensing (not sink) node."""

    def __init__(self, address, name=None):
        super().__init__(address, name)

    def get_next_hop_node(self):
        """Returns the node to route data."""
        pass


class SinkNode(_Node):
    """Defines attributes and methods specific for a sink node."""

    def __init__(self, address, name=None):
        super().__init__(address, name)
        pass


class _SimulationNode(_Node):
    """Extends Node class in order to simulate."""

    def __init__(self, address, name=None):
        super().__init__(address, name)


class SimulationSensingNode(SensingNode, _SimulationNode):
    """Extends SensingNode and SimulationNode class in order to simulate."""

    def __init__(self, address, name=None):
        super().__init__(address, name)


class SimulationSinkNode(SinkNode, _SimulationNode):
    """Extends SinkNode and SimulationNode class in order to simulate."""

    def __init__(self, address, name=None):
        super().__init__(address, name)


def convert_to_simulation_nodes(nodes):
    """Returns simulation nodes from regular nodes."""
    simulation_nodes = []
    for node in nodes:
        address = node.address
        name = node.name
        if isinstance(node, SensingNode):
            simulation_node = SimulationSensingNode(address, name)
        elif isinstance(node, SinkNode):
            simulation_node = SimulationSinkNode(address, name)
        else:
            raise AttributeError('Class of node is not correct')
        simulation_nodes.append(simulation_node)
    return simulation_nodes
