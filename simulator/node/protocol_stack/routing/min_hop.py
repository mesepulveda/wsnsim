"""Implements min-hop routing protocol/metric."""
from typing import Callable, Generator, Any, Optional

from simpy import Environment, Event, Resource

from simulator.auxiliary_functions import get_components_of_message
from ..routing.base_routing_protocol import RoutingProtocol


def _find_min_hop_neighbour(neighbours):
    # todo: complete it properly
    if neighbours:
        return neighbours[0]


class _MinHopRouting(RoutingProtocol):
    """Private base class for the min-hop routing."""

    def __init__(self,
                 address: str,
                 radio: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, radio, env)
        self.neighbours = set()
        # noinspection PyArgumentEqualDefault
        self._output_queue = Resource(env, capacity=1)

    def _send_data_to_medium(self, data: str) -> Generator[Event, Any, Any]:
        yield self.env.process(self._radio(data))

    def add_to_output_queue(self, message: str, destination: str) \
            -> Generator[Event, Any, Any]:
        """Adds a message to the output queue."""
        with self._output_queue.request() as req:
            print(round(self.env.now, 2), self.address, 'Message:', message,
                  'entered output queue')
            yield req
            yield self.env.process(self._send_packet(message, destination))

    def _send_packet(self, message: str, destination: str) \
            -> Generator[Event, Any, Any]:
        """Method to send a message to a destination."""
        next_hop_address = self._choose_next_hop_address(destination)
        if next_hop_address is None:
            # First we need to discover neighbours
            self._find_neighbours()
            yield self.env.process(self._send_packet(message, destination))
        data = '{},{},{}'.format(self.address, next_hop_address, message)
        print(round(self.env.now, 2),
              '{0} sending: {1}'.format(self.address, data))
        yield self.env.process(self._send_data_to_medium(data))

    def receive_packet(self, message: str) -> Generator[Event, Any, Any]:
        """Method called when a packet arrives."""
        print(round(self.env.now, 2),
              '{0} received: {1}'.format(self.address, message))
        origin_address, _, data = get_components_of_message(message)
        self.neighbours.add(origin_address)
        if data != 'ACK':
            yield self.env.process(self._send_packet('ACK', origin_address))

    def _choose_next_hop_address(self, destination: str) -> Optional[str]:
        """Returns one or a list of nodes to route data."""
        if destination == 'broadcast':
            return ''
        elif destination in self.neighbours:
            return destination
        elif destination == 'sink':
            min_hop_neighbour = _find_min_hop_neighbour(self.neighbours)
            return min_hop_neighbour.address
        return None

    def _find_neighbours(self) -> None:
        """Method to discover neighbours."""
        # send 'hello'
        self._send_data_to_medium('{},{},{}'.format(self.address, '', 'hello'))
        # wait until the neighbours answer...


class MinHopRouting(_MinHopRouting):
    """Class of min-hop routing protocol for sensing nodes."""

    def __init__(self,
                 address: str,
                 radio: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, radio, env)


class MinHopRoutingSink(_MinHopRouting):
    """Class of min-hop routing protocol for sink node."""

    def __init__(self,
                 address: str,
                 radio: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, radio, env)
