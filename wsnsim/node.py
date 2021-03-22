"""Everything related with the simulation of a node."""

from typing import Union, Optional, Callable, Iterable, Type, Generator, Any

from simpy import Environment, Event

from .routing import MinHopRouting, MinHopRoutingSink, ETX, ETXSink, DAPRouting, DAPRoutingSink
from .routing import RoutingProtocol


class _Node:
    """Defines attributes and methods needed in both sink and sensing nodes."""

    def __init__(self, address: str, name: Optional[str] = None) -> None:
        self.address = address
        if name:
            self.name = name
        else:
            self.name = self.address

    def __eq__(self, other):
        return self.address == other.address

    def __hash__(self):
        return hash(self.address)

    def __repr__(self):
        return f'(Address: {self.address}, Name: {self.name})'

    def __str__(self):
        return f'Node {self.name}'


class SensingNode(_Node):
    """Defines attributes and methods of a regular sensing (not sink) node."""

    def __init__(self, address: str, name: Optional[str] = None,
                 sensing_period: Optional[float] = 60*60,
                 sensing_offset: Optional[float] = 60) -> None:
        super().__init__(address, name)
        self.sensing_offset = sensing_offset
        self.sensing_period = sensing_period


class SinkNode(_Node):
    """Defines attributes and methods specific for a sink node."""

    def __init__(self, address: str, name: Optional[str] = None) -> None:
        super().__init__(address, name)


class _SimulationNode(_Node):
    """Extends Node class in order to simulate."""

    def __init__(self, address: str, name: str,
                 routing_protocol: Type[RoutingProtocol],
                 access_function: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, name)
        self.routing_protocol = routing_protocol(address, access_function, env)
        self.env = env

    def _send_message(self, message: str, destination: str) \
            -> Generator[Event, Any, Any]:
        """Sends a message to sink or neighbour nodes."""
        # Pass the message to the routing protocol
        event = self.routing_protocol.add_to_output_queue(message, destination)
        yield self.env.process(event)

    def receive_message(self, message: str) -> None:
        """Receive a message from another node."""
        # Pass the message to the routing protocol in order to analyze it
        self.routing_protocol.receive_packet(message)

    def _print_info(self, info: str) -> None:
        """Print information with format."""
        print(f'{self.env.now:.2f} | {self.address} | {info}')


class SimulationSensingNode(_SimulationNode, SensingNode):
    """Extends SensingNode and SimulationNode class in order to simulate."""

    def __init__(self, address: str, name: str,
                 routing_protocol: Type[RoutingProtocol],
                 access_function: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment, sensing_period: float,
                 sensing_offset: float) -> None:
        _SimulationNode.__init__(self, address, name, routing_protocol,
                                 access_function, env)
        SensingNode.__init__(self, address, sensing_period=sensing_period,
                             sensing_offset=sensing_offset)
        self.env.process(self._main_routine())

    def _main_routine(self) -> Generator[Event, Any, Any]:
        """Main routine of the nodes."""
        self._print_info('is awake')
        # Start routing protocol setup routine
        self.env.process(self.routing_protocol.setup())
        # Wait for the sensing offset
        yield self.env.timeout(self.sensing_offset)
        while True:
            # Sensing every 15 minutes
            event = self._send_message(self._format_measurement('X'), 'sink')
            self.env.process(event)
            yield self.env.timeout(self.sensing_period)

    def _format_measurement(self, measurement: str) -> str:
        """Formats the measurement to include address and timestamp."""
        return f'{self.address}/{measurement}/{self.env.now:.2f}'


class SimulationSinkNode(_SimulationNode, SinkNode):
    """Extends SinkNode and SimulationNode class in order to simulate."""

    def __init__(self, address: str, name: str,
                 routing_protocol: Type[RoutingProtocol],
                 access_function: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        _SimulationNode.__init__(self, address, name, routing_protocol,
                                 access_function, env)
        self.env.process(self._main_routine())

    def _main_routine(self) -> Generator[Event, Any, Any]:
        """Main routine of the nodes."""
        self._print_info('is awake')
        # Start routing protocol setup routine
        self.env.process(self.routing_protocol.setup())
        # noinspection PyArgumentEqualDefault
        yield self.env.timeout(0)


Node = Union[SensingNode, SinkNode]
SimulationNode = Union[SimulationSinkNode, SimulationSensingNode]


def convert_to_simulation_nodes(
        regular_nodes: Iterable[Node],
        routing_protocol: str,
        deadline: float,
        send_data_function: Callable[[str], Generator[Event, Any, Any]],
        env: Environment) \
        -> Iterable[SimulationNode]:
    """Returns simulation nodes from regular nodes."""
    simulation_nodes = []
    if routing_protocol == 'min-hop':
        routing_sensing_node = MinHopRouting
        routing_sink_node = MinHopRoutingSink
    elif routing_protocol == "etx":
        routing_sensing_node = ETX
        routing_sink_node = ETXSink
    elif routing_protocol == 'dap':
        routing_sensing_node = DAPRouting
        routing_sink_node = DAPRoutingSink
        routing_sensing_node.deadline = deadline
        routing_sink_node.deadline = deadline
    else:  # Default routing protocol
        raise ValueError(f"{routing_protocol} is not a valid protocol")
    for node in regular_nodes:
        if isinstance(node, SensingNode):
            simulation_node = SimulationSensingNode(node.address,
                                                    node.name,
                                                    routing_sensing_node,
                                                    send_data_function,
                                                    env,
                                                    node.sensing_period,
                                                    node.sensing_offset)
        elif isinstance(node, SinkNode):
            simulation_node = SimulationSinkNode(node.address,
                                                 node.name,
                                                 routing_sink_node,
                                                 send_data_function,
                                                 env)
        else:
            raise AttributeError('Class of node is not correct')
        simulation_nodes.append(simulation_node)
    return simulation_nodes


def get_equivalent_simulation_node(
        nodes: Iterable[Node],
        simulation_nodes: Iterable[SimulationNode]) \
        -> Iterable[SimulationNode]:
    """Returns the equivalent simulation node of a list of nodes."""
    equivalent_simulation_nodes = []
    for node in nodes:
        equivalent_node = _get_equivalent_node(node, simulation_nodes)
        equivalent_simulation_nodes.append(equivalent_node)
    return equivalent_simulation_nodes


def _get_equivalent_node(
        node: Node,
        simulation_nodes: Iterable[SimulationNode]) \
        -> SimulationNode:
    """Returns the equivalent simulation node of one node."""
    for simulation_node in simulation_nodes:
        if node.address == simulation_node.address:
            return simulation_node


def get_sink_node(nodes: Iterable[SimulationNode]) -> SimulationSinkNode:
    """Returns the sink node from a list of Simulation Nodes."""
    for node in nodes:
        if isinstance(node, SimulationSinkNode):
            return node
    Exception("There was not a Sink Node in the list.")
