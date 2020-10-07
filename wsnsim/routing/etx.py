"""Implements ETX routing protocol/metric."""

from typing import Callable, Generator, Any, Optional, Dict
from random import choice
from statistics import mean

from simpy import Environment, Event

from .base_routing_protocol import RoutingProtocol
from ..auxiliary_functions import get_components_of_message, is_hello_message

"""
ETX:

1) Every node has a default etx (etx).
2) Every node calculates link statistics (link_etx).
3) A sharing phase start calculating total_etx for every neighbour and updating
the own etx to min(total_etx) and sharing again...

"""


class Neighbour:
    """Definition of a neighbour in the context of ETX routing."""

    def __init__(self, address: str, etx: float = 999999) -> None:
        self.address = address
        self.etx = etx
        self.link_etx = []
        self.total_etx = etx

    def update_etx(self, etx: float) -> None:
        """Updates the etx and total_etx attributes."""
        self.etx = etx
        if self.link_etx:
            self.total_etx = etx + mean(self.link_etx)
        else:
            self.total_etx = etx

    def update_link_etx(self, link_etx: float) -> None:
        """Updates the link_etx and total_etx attributes."""
        self.link_etx.append(link_etx)
        self.total_etx = self.etx + mean(self.link_etx)

    def __repr__(self):
        link_etx = 0
        if self.link_etx:
            link_etx = mean(self.link_etx)
        return f'(Address: {self.address}, ETX: {self.etx}), ' \
               f'Link ETX: {link_etx}, Total ETX: {self.total_etx}'

    def __str__(self):
        link_etx = 0
        if self.link_etx:
            link_etx = mean(self.link_etx)
        return f'(Address: {self.address}, ETX: {self.etx}), ' \
               f'Link ETX: {link_etx}, Total ETX: {self.total_etx}'

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
    _neighbours: Dict[str, Neighbour]

    def __init__(self,
                 address: str,
                 radio: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, radio, env)
        self.etx = 999999
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
        prove_packet = destination not in ['', 'broadcast', 'sink']
        next_hop_address = self._choose_next_hop_address(destination)
        if next_hop_address is None:
            raise Exception('No next hop address was returned to route·')
        data = '{},{},{}'.format(self.address, next_hop_address, message)
        self._print_info(f'sending: {data}')
        self._log_message_sending(data, destination)
        if prove_packet:
            start_time = self.env.now
        yield self.env.process(self._radio(data))
        if prove_packet:
            end_time = self.env.now
            delay = end_time - start_time
            self._neighbours[destination].update_link_etx(delay)
        self._log_message_sent(data, destination)

    def _analyze_hello_message(self, origin_address: str) -> None:
        """Checks information of Hello message."""
        new_neighbour = Neighbour(origin_address)
        if new_neighbour.address not in self._neighbours:
            self._neighbours[new_neighbour.address] = new_neighbour
            self.env.process(self.add_to_output_queue(f'Hello', 'broadcast'))

    def _choose_next_hop_address(self, destination: str) -> Optional[str]:
        """Returns one or a list of nodes to route data."""
        if destination == 'broadcast' or destination == '':
            return ''
        elif destination == 'sink':
            min_etx_address = _find_min_etx_neighbour(self._neighbours)
            return min_etx_address
        elif destination in self._neighbours:
            return destination
        return None


class ETX(_ETX):
    """Class of min-hop routing protocol for sensing nodes."""

    def __init__(self,
                 address: str,
                 radio: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, radio, env)

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
        self._analyze_hello_message(origin_address)


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
        yield self.env.process(self.add_to_output_queue(f'Hello', 'broadcast'))

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
        self._analyze_hello_message(origin_address)