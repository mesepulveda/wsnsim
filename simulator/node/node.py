"""Everything related with the simulation of a node."""
import random
import simpy

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

    def __init__(self, address, name, routing_protocol,
                 env: simpy.Environment):
        super().__init__(address, name)
        self.routing_protocol = routing_protocol(address)
        self.env = env

    def setup_medium_access(self, access_function):
        """Associates the medium access function with the node."""
        self.routing_protocol.setup_access_function(access_function)
        # todo: clear this dependency, the medium should be setup in the init
        self.env.process(self._main_routine())

    def _send_message(self, message, destination):
        """Sends a message to sink or neighbour nodes."""
        return self.routing_protocol.send_packet(message, destination)

    def receive_message(self, message):
        """Receive a message from another node."""
        return self.routing_protocol.receive_packet(message)

    def _main_routine(self):
        """Main routine of the nodes."""
        # random delay between 0 and 10
        yield self.env.timeout(random.random() * 10)
        print(round(self.env.now, 2), self.name, 'is awake')
        yield self.env.timeout(15)  # Wait 15 second until every node wakes up
        self._send_message('Hello', 'broadcast')


class SimulationSensingNode(_SimulationNode, SensingNode):
    """Extends SensingNode and SimulationNode class in order to simulate."""

    def __init__(self, address, name, routing_protocol,
                 env: simpy.Environment):
        super().__init__(address, name, routing_protocol, env)


class SimulationSinkNode(_SimulationNode, SinkNode):
    """Extends SinkNode and SimulationNode class in order to simulate."""

    def __init__(self, address, name, routing_protocol,
                 env: simpy.Environment):
        super().__init__(address, name, routing_protocol, env)


def convert_to_simulation_nodes(regular_nodes, routing_protocol, env):
    """Returns simulation nodes from regular nodes."""
    simulation_nodes = []
    if routing_protocol == 'min-hop':
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
                                                    routing_sensing_node,
                                                    env)
        elif isinstance(node, SinkNode):
            simulation_node = SimulationSinkNode(address,
                                                 name,
                                                 routing_sink_node,
                                                 env)
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
