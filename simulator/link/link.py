"""Everything related with the simulation of a link."""
from simulator.auxiliary_functions import ensure_positive_value
from simulator.node import get_equivalent_simulation_node


class Link:
    """Relates two nodes in a physical medium."""

    def __init__(self, node_1, node_2, delay_function):
        self.nodes = sorted([node_1, node_2], key=lambda node: node.address)
        self._delay_function = delay_function

    @ensure_positive_value
    def get_delay(self):
        """Returns a realization of delay value of the link."""
        return self._delay_function()

    def get_destination(self, origin_address):
        """Returns the destination node of the link from the origin address."""
        origin_node = None
        for node in self.nodes:
            if node.address == origin_address:
                origin_node = node
        if origin_node is None:
            return None
        destination_node = (set(self.nodes) - {origin_node}).pop()
        return destination_node

    def __repr__(self):
        return '{0}, {1}'.format(*[node.address for node in self.nodes])

    def __str__(self):
        return '{0}, {1}'.format(*[node.address for node in self.nodes])


class SimulationLink(Link):
    """Extends Link class in order to simulate."""

    def __init__(self, node_1, node_2, delay_function):
        super().__init__(node_1, node_2, delay_function)


def convert_to_simulation_links(links, simulation_nodes):
    """Returns simulation links from regular links."""
    simulation_links = []
    for link in links:
        simulation_equivalent_nodes = \
            get_equivalent_simulation_node(link.nodes, simulation_nodes)
        # noinspection PyProtectedMember
        simulation_link = \
            SimulationLink(*simulation_equivalent_nodes, link._delay_function)
        simulation_links.append(simulation_link)
    return simulation_links


def get_link_(origin_address, destination_address, links):
    """Returns a link, if exist, that relates two nodes."""
    for link in links:
        nodes_addresses = {node.address for node in link.nodes}
        if nodes_addresses == {origin_address, destination_address}:
            return link
    return None


def get_all_links_of_node(node_address, links):
    """Returns all the links of a node."""
    node_links = []
    for link in links:
        link_addresses = {node.address for node in link.nodes}
        if node_address in link_addresses:
            node_links.append(link)
    return node_links
