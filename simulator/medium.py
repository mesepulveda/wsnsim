"""Implements the wireless medium."""
from simulator.auxiliary_functions import get_components_of_message
from simulator.link import get_all_links_of_node


class Medium:
    """Abstraction of the Physical Medium to communicate in Radio Frequency."""

    def __init__(self, env):
        self.env = env
        self._links = None
        
    def setup_links(self, links):
        """Updates the links used by the medium object."""
        self._links = links

    def send_data_to_medium(self, data):
        """Sends the data to the medium in order to reach other nodes."""
        origin_address, _, _ = get_components_of_message(data)
        links = get_all_links_of_node(origin_address, self._links)
        for link in links:
            destination_node = link.get_destination(origin_address)
            yield self.env.timeout(link.get_delay())
            self.env.process(destination_node.receive_message(data))
