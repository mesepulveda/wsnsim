"""Implements the wireless medium."""
from simulator.auxiliary_functions import get_components_of_message
from simulator.link import get_all_links_of_node


def setup_nodes_medium_access(simulation_nodes, send_data_to_medium):
    """Associates the nodes with a function to access the medium."""
    for node in simulation_nodes:
        node.setup_medium_access(send_data_to_medium)


class Medium:
    """Abstraction of the Physical Medium to communicate in Radio Frequency."""

    def __init__(self, links):
        self.links = links

    def send_data_to_medium(self, data):
        """Sends the data to the medium in order to reach other nodes."""
        origin_address, _, _ = get_components_of_message(data)
        links = get_all_links_of_node(origin_address, self.links)
        for link in links:
            destination_node = link.get_destination(origin_address)
            destination_node.receive_message(data)
