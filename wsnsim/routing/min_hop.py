"""Implements min-hop routing protocol/metric."""

from typing import Callable, Generator, Any, Optional, Dict
from random import choice

from simpy import Environment, Event

from ..auxiliary_functions import get_components_of_message
from .base_routing_protocol import RoutingProtocol


class Neighbour:
    """Definition of a neighbour in the context of min-hop routing."""

    def __init__(self, address: str, hop_count: int) -> None:
        self.address = address
        self.hop_count = hop_count

    def update_hop_count(self, hop_count: int) -> None:
        """Updates the hop count, if corresponds, of a neighbour."""
        if hop_count < self.hop_count:
            self.hop_count = hop_count

    def __repr__(self):
        return f'(Address: {self.address}, Hops: {self.hop_count})'

    def __str__(self):
        return f'(Address: {self.address}, Hops: {self.hop_count})'

    def __eq__(self, other):
        return other.address == self.address

    def __hash__(self):
        return hash(self.address)


def _find_min_hop_neighbour(neighbours_dict: Dict[str, Neighbour]) -> str:
    """Returns the address of the selected forwarder with min-hop to sink."""
    neighbours = neighbours_dict.values()
    min_hop = min({neighbour.hop_count for neighbour in neighbours})
    min_hop_neighbours = [n for n in neighbours if n.hop_count == min_hop]
    neighbour_selected = choice(min_hop_neighbours)
    return neighbour_selected.address


class _MinHopRouting(RoutingProtocol):
    """Private base class for the min-hop routing."""

    def __init__(self,
                 address: str,
                 radio: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, radio, env)
        self.hop_count = 99
        self._neighbours = dict()

    def update_hop_count(self, hop_count: int) -> bool:
        """Updates the node hop count, adding 1 to the neighbour count."""
        tentative_hop_count = hop_count + 1
        if tentative_hop_count < self.hop_count:
            self.hop_count = tentative_hop_count
            return True
        return False

    def add_to_output_queue(self, message: str, destination: str) \
            -> Generator[Event, Any, Any]:
        """Adds a message to the output queue."""
        self._log_output_queue_message(message, destination)
        with self._output_queue.request() as req:
            yield req
            yield self.env.process(self._send_packet(message, destination))

    def _send_packet(self, message: str, destination: str) \
            -> Generator[Event, Any, Any]:
        """Method to send a message to a destination."""
        next_hop_address = self._choose_next_hop_address(destination)
        if next_hop_address is None:
            raise Exception('No next hop address was returned to route·')
        data = '{},{},{}'.format(self.address, next_hop_address, message)
        self._print_info('{0} sending: {1}'.format(self.address, data))
        yield self.env.process(self._radio(data))

    def _analyze_hello_message(self, info: str, origin_address: str) -> None:
        """Checks information of Hello message."""
        new_neighbour_hop_count = int(info.split('+')[1])
        new_neighbour = Neighbour(origin_address, new_neighbour_hop_count)
        if new_neighbour.address not in self._neighbours:
            self._neighbours[new_neighbour.address] = new_neighbour
            self.update_hop_count(new_neighbour_hop_count)
            self.env.process(self.add_to_output_queue(
                f'Hello+{self.hop_count}', 'broadcast'))
            return
        # In case the neighbour exists, check if the hop count is the same
        # if it is the same, nothing must be done, if it is different, must
        # be updated, check if the own hop count changes and, if it does change
        # should be shared
        old_version_neighbour = self._neighbours[new_neighbour.address]
        if old_version_neighbour.hop_count != new_neighbour.hop_count:
            self._neighbours[new_neighbour.address] = new_neighbour
            self._print_info(f'Node {origin_address} is updated neighbour with hop '
                  f'count {new_neighbour_hop_count}')
            new_value = self.update_hop_count(new_neighbour_hop_count)
            if new_value:
                # Share new hop count
                self.env.process(self.add_to_output_queue(
                    f'Hello+{self.hop_count}', 'broadcast'))

    def _choose_next_hop_address(self, destination: str) -> Optional[str]:
        """Returns one or a list of nodes to route data."""
        if destination == 'broadcast' or destination == '':
            return ''
        elif destination == 'sink':
            min_hop_address = _find_min_hop_neighbour(self._neighbours)
            return min_hop_address
        return None


class MinHopRouting(_MinHopRouting):
    """Class of min-hop routing protocol for sensing nodes."""

    def __init__(self,
                 address: str,
                 radio: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, radio, env)
        self.hop_count = 99

    def receive_packet(self, message: str) -> None:
        """Method called when a packet arrives."""
        self._log_received_message(message)
        self._print_info('{0} received: {1}'.format(self.address, message))
        origin_address, destination_address, info = \
            get_components_of_message(message)
        assert destination_address == self.address or destination_address == ''
        if '+' not in info:
            # It is not a hello message, so it should be forwarded
            self.env.process(self.add_to_output_queue(info, 'sink'))
            return
        # If '+' in the message, it is a hello message
        self._analyze_hello_message(info, origin_address)


class MinHopRoutingSink(_MinHopRouting):
    """Class of min-hop routing protocol for sink node."""

    def __init__(self,
                 address: str,
                 radio: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, radio, env)
        self.hop_count = 0

    def setup(self) -> Generator[Event, Any, Any]:
        """Initiates the neighbours discovery with hop count."""
        yield self.env.process(self.add_to_output_queue(
            f'Hello+{self.hop_count}', 'broadcast'))

    def receive_packet(self, message: str) -> None:
        """Method called when a packet arrives."""
        self._log_received_message(message)
        self._print_info('{0} received: {1}'.format(self.address, message))
        origin_address, destination_address, info = \
            get_components_of_message(message)
        assert destination_address == self.address or destination_address == ''
        if '+' not in info:
            # It is not a hello message, so it reached the sink node
            self._print_info(f'Message: {info} reached sink node')
            return
        # If '+' in the message, it is a hello message
        self._analyze_hello_message(info, origin_address)
