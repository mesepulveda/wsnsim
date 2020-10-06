"""Implements ETX routing protocol/metric."""

from typing import Callable, Generator, Any, Optional, Dict
from random import choice

from simpy import Environment, Event

from .base_routing_protocol import RoutingProtocol

"""
ETX:

1) Every node has a default etx (etx).
2) Every node calculates link statistics (link_etx).
3) A sharing phase start calculating total_etx for every neighbour and updating
the own etx to min(total_etx) and sharing again...

"""


class Neighbour:
    """Definition of a neighbour in the context of ETX routing."""

    def __init__(self, address: str, etx: float, link_etx: float) -> None:
        self.address = address
        self.etx = etx
        self.link_etx = link_etx
        self.total_etx = etx + link_etx

    def update_etx(self, etx: float) -> None:
        """Updates the etx and total_etx attributes."""
        self.etx = etx
        self.total_etx = etx + self.link_etx

    def update_link_etx(self, link_etx: float) -> None:
        """Updates the link_etx and total_etx attributes."""
        self.link_etx = link_etx
        self.total_etx = self.etx + link_etx

    def __repr__(self):
        return f'(Address: {self.address}, ETX: {self.etx}), ' \
               f'Link ETX: {self.link_etx}, Total ETX: {self.total_etx}'

    def __str__(self):
        return f'(Address: {self.address}, ETX: {self.etx}), ' \
               f'Link ETX: {self.link_etx}, Total ETX: {self.total_etx}'

    def __eq__(self, other):
        return other.address == self.address

    def __hash__(self):
        return hash(self.address)


def _find_min_etx_neighbour(neighbours_dict: Dict[str, Neighbour]) -> str:
    """Returns the address of the selected forwarder with minimum ETX to
    sink."""
    neighbours = neighbours_dict.values()
    min_total_etx = min({neighbour.total_etx for neighbour in neighbours})
    min_etx_neighbours = [n for n in neighbours if n.etx == min_total_etx]
    neighbour_selected = choice(min_etx_neighbours)
    return neighbour_selected.address


class _ETX(RoutingProtocol):
    """Implements methods to both sink and sensing nodes."""

    def __init__(self,
                 address: str,
                 radio: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, radio, env)
        self.etx = 9999999
        self._neighbours = dict()

    def update_etx(self, tentative_etx: float) -> bool:
        """Updates the ETX count."""
        if tentative_etx < self.etx:
            self.etx = tentative_etx
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
        self._print_info(f'sending: {data}')
        self._log_message_sending(data, destination)
        yield self.env.process(self._radio(data))
        self._log_message_sent(data, destination)

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
            self._print_info(f'Node {origin_address} is updated neighbour with'
                             f'hop count {new_neighbour_hop_count}')
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
            min_etx_address = _find_min_etx_neighbour(self._neighbours)
            return min_etx_address
        return None


class ETX(_ETX):
    """Class of min-hop routing protocol for sensing nodes."""

    def __init__(self,
                 address: str,
                 radio: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, radio, env)
        self.etx = 60*60

    def receive_packet(self, message: str) -> None:
        """Method called when a packet arrives."""
        self._log_received_message(message)
        self._print_info(f'received: {message}')
        origin_address, destination_address, info = \
            get_components_of_message(message)
        assert destination_address == self.address or destination_address == ''
        if not is_hello_message(info):
            # It is not a hello message, so it should be forwarded
            self.env.process(self.add_to_output_queue(info, 'sink'))
            return
        # It is a hello message
        self._analyze_hello_message(info, origin_address)


class ETXSink(_ETX):
    """Class of min-hop routing protocol for sink node."""

    def __init__(self,
                 address: str,
                 radio: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, radio, env)
        self.etx = 0

    def setup(self) -> Generator[Event, Any, Any]:
        """Initiates the neighbours discovery with hop count."""
        yield self.env.process(self.add_to_output_queue(
            f'Hello+{self.hop_count}', 'broadcast'))

    def receive_packet(self, message: str) -> None:
        """Method called when a packet arrives."""
        self._log_received_message(message)
        self._print_info(f'received: {message}')
        origin_address, destination_address, info = \
            get_components_of_message(message)
        assert destination_address == self.address or destination_address == ''
        if not is_hello_message(info):
            # It is not a hello message, so it reached the sink node
            self._print_info(f'message: {info} reached sink node')
            return
        # It is a hello message
        self._analyze_hello_message(info, origin_address)
