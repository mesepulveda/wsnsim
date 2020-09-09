"""Implements the wireless medium."""
from typing import Iterable, Generator, Any

from simpy import Environment, Event

from simulator.auxiliary_functions import get_components_of_message
from simulator.link import SimulationLink, get_all_links_of_node, \
    get_link_between_nodes


class Medium:
    """Abstraction of the Physical Medium to communicate in Radio Frequency."""

    def __init__(self, env: Environment) -> None:
        self.env = env
        self._links = None

    def setup_links(self, links: Iterable[SimulationLink]) -> None:
        """Updates the links used by the medium object."""
        self._links = links

    def send_data_to_medium(self, data: str) -> Generator[Event, Any, Any]:
        """Sends the data to the medium in order to reach other nodes."""
        origin_address, destination_address, _ = \
            get_components_of_message(data)
        if destination_address == '':
            # In case of broadcast, the messages are not delayed
            links = get_all_links_of_node(origin_address, self._links)
            for link in links:
                destination = link.get_destination(origin_address)
                # noinspection PyArgumentEqualDefault
                yield self.env.timeout(0)
                destination.receive_message(data)
        else:
            # In case of message to specific node, the message is delayed
            link = get_link_between_nodes(origin_address,
                                          destination_address, self._links)
            destination = link.get_destination(origin_address)
            yield self.env.timeout(link.get_delay())
            destination.receive_message(data)

