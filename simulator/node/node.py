"""Everything related with the simulation of a node."""
from .protocol_stack.routing.min_hop import MinHopRouting, MinHopRoutingSink


class _Node:
    """Defines attributes and methods needed in both sink and sensing nodes."""

    def __init__(self, address, name=None):
        self.address = str(address)
        if name:
            self.name = str(name)
        else:
            self.name = self.address

    def __repr__(self):
        return '{0}, {1}'.format(self.address, self.name)

    def __str__(self):
        return '{0}, {1}'.format(self.address, self.name)


class SensingNode(_Node):
    """Defines attributes and methods of a regular sensing (not sink) node."""

    def __init__(self, address, name=None):
        super().__init__(address, name)


class SinkNode(_Node):
    """Defines attributes and methods specific for a sink node."""

    def __init__(self, address, name=None):
        super().__init__(address, name)


class _SimulationNode(_Node):
    """Extends Node class in order to simulate."""

    def __init__(self, address, name, routing_protocol):
        super().__init__(address, name)
        self.routing_protocol = routing_protocol(address)

    def setup_medium_access(self, access_function):
        """Associates the medium access function with the node."""
        self.routing_protocol.setup_access_function(access_function)

    def send_message(self, message, destination):
        """Sends a message to sink or neighbour nodes."""
        return self.routing_protocol.send_packet(message, destination)

    def receive_message(self, message):
        """Receive a message from another node."""
        return self.routing_protocol.receive_packet(message)

    def clear_simulation(self):
        """Clears logs of simulations."""
        # todo: implement it
        pass


class SimulationSensingNode(_SimulationNode, SensingNode):
    """Extends SensingNode and SimulationNode class in order to simulate."""

    def __init__(self, address, name, routing_protocol):
        super().__init__(address, name, routing_protocol)

    def clear_simulation(self):
        """Clears logs of simulations."""
        # todo: implement it
        super().clear_simulation()
        pass


class SimulationSinkNode(_SimulationNode, SinkNode):
    """Extends SinkNode and SimulationNode class in order to simulate."""

    def __init__(self, address, name, routing_protocol):
        super().__init__(address, name, routing_protocol)

    def clear_simulation(self):
        """Clears logs of simulations."""
        # todo: implement it
        super().clear_simulation()
        pass


def convert_to_simulation_nodes(regular_nodes, routing_stack_name):
    """Returns simulation nodes from regular nodes."""
    simulation_nodes = []
    if routing_stack_name == 'min-hop':
        routing_sensing_node = MinHopRouting
        routing_sink_node = MinHopRoutingSink
    else:  # Default routing protocol
        routing_sensing_node = MinHopRouting
        routing_sink_node = MinHopRoutingSink
    for node in regular_nodes:
        address = node.address
        name = node.name
        if isinstance(node, SensingNode):
            simulation_node = SimulationSensingNode(address,
                                                    name,
                                                    routing_sensing_node)
        elif isinstance(node, SinkNode):
            simulation_node = SimulationSinkNode(address,
                                                 name,
                                                 routing_sink_node)
        else:
            raise AttributeError('Class of node is not correct')
        simulation_nodes.append(simulation_node)
    return simulation_nodes


def get_equivalent_simulation_node(nodes, simulation_nodes):
    """Returns the equivalent simulation node of one or many nodes."""
    # If it is only one object
    if isinstance(nodes, (SensingNode, SinkNode)):
        return _get_equivalent_node(nodes, simulation_nodes)
    # If it is a list of objects
    equivalent_simulation_nodes = []
    for node in nodes:
        equivalent_node = _get_equivalent_node(node, simulation_nodes)
        equivalent_simulation_nodes.append(equivalent_node)
    return equivalent_simulation_nodes


def _get_equivalent_node(node, simulation_nodes):
    """Returns the equivalent simulation node of one node."""
    for simulation_node in simulation_nodes:
        if node.address == simulation_node.address:
            return simulation_node
