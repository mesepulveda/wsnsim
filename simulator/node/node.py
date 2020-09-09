"""Everything related with the simulation of a node."""
from typing import Union, Optional, Callable, Iterable, Type, Generator, Any
import random

from simpy import Environment, Event

from .protocol_stack.routing.min_hop import MinHopRouting, MinHopRoutingSink
from .protocol_stack.routing.base_routing_protocol import RoutingProtocol


class _Node:
    """Defines attributes and methods needed in both sink and sensing nodes."""

    def __init__(self, address: str, name: Optional[str] = None) -> None:
        self.address = address
        if name:
            self.name = name
        else:
            self.name = self.address

    def __repr__(self):
        return '{0}, {1}'.format(self.address, self.name)

    def __str__(self):
        return '{0}, {1}'.format(self.address, self.name)


class SensingNode(_Node):
    """Defines attributes and methods of a regular sensing (not sink) node."""

    def __init__(self, address: str, name: Optional[str] = None) -> None:
        super().__init__(address, name)


class SinkNode(_Node):
    """Defines attributes and methods specific for a sink node."""

    def __init__(self, address: str, name: Optional[str] = None) -> None:
        super().__init__(address, name)


Node = Union[SensingNode, SinkNode]


class _SimulationNode(_Node):
    """Extends Node class in order to simulate."""

    def __init__(self, address: str, name: str,
                 routing_protocol: Type[RoutingProtocol],
                 access_function: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, name)
        self._access_function = access_function
        self.routing_protocol = routing_protocol(address, self._radio, env)
        self.env = env
        self.env.process(self._main_routine())

    def _radio(self, data: str) -> Generator[Event, Any, Any]:
        yield self.env.process(self._access_function(data))

    def _send_message(self, message: str, destination: str)\
            -> Generator[Event, Any, Any]:
        """Sends a message to sink or neighbour nodes."""
        # Pass the message to the routing protocol
        yield self.env.process(self.routing_protocol.add_to_output_queue(
            message,
            destination))

    def receive_message(self, message: str) -> None:
        """Receive a message from another node."""
        # Pass the message to the routing protocol in order to analyze it
        self.routing_protocol.receive_packet(message)

    def _main_routine(self) -> Generator[Event, Any, Any]:
        """Main routine of the nodes."""
        # random delay between 0 and 10
        yield self.env.timeout(random.random() * 10)
        print(round(self.env.now, 2), self.name, 'is awake')
        yield self.env.timeout(15)  # Wait 15 second until every node wakes up
        self.env.process(self._send_message('Hello', 'broadcast'))


class SimulationSensingNode(_SimulationNode, SensingNode):
    """Extends SensingNode and SimulationNode class in order to simulate."""

    def __init__(self, address: str, name: str,
                 routing_protocol: Type[RoutingProtocol],
                 access_function: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, name, routing_protocol, access_function,
                         env)


class SimulationSinkNode(_SimulationNode, SinkNode):
    """Extends SinkNode and SimulationNode class in order to simulate."""

    def __init__(self, address: str, name: str,
                 routing_protocol: Type[RoutingProtocol],
                 access_function: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, name, routing_protocol, access_function,
                         env)


SimulationNode = Union[SimulationSinkNode, SimulationSensingNode]


def convert_to_simulation_nodes(
        regular_nodes: Iterable[Node],
        routing_protocol: str,
        send_data_function: Callable[[str], Generator[Event, Any, Any]],
        env: Environment) -> Iterable[SimulationNode]:
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
                                                    send_data_function,
                                                    env)
        elif isinstance(node, SinkNode):
            simulation_node = SimulationSinkNode(address,
                                                 name,
                                                 routing_sink_node,
                                                 send_data_function,
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
