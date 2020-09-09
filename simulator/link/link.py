"""Everything related with the simulation of a link."""
from typing import Callable, Iterable
from simulator.auxiliary_functions import ensure_positive_value
from simulator.node import Node, SimulationNode, get_equivalent_simulation_node


class Link:
    """Relates two nodes in a physical medium."""

    def __init__(self, node_1: Node, node_2: Node,
                 delay_function: Callable[[], float]) -> None:
        self.nodes = sorted([node_1, node_2], key=lambda node: node.address)
        self._delay_function = delay_function

    @ensure_positive_value
    def get_delay(self) -> float:
        """Returns a realization of delay value of the link."""
        return self._delay_function()

    def __repr__(self) -> str:
        return '{0}, {1}'.format(*[node.address for node in self.nodes])

    def __str__(self) -> str:
        return '{0}, {1}'.format(*[node.address for node in self.nodes])


class SimulationLink(Link):
    """Extends Link class in order to simulate."""

    def __init__(self, node_1: SimulationNode, node_2: SimulationNode,
                 delay_function: Callable[[], float]) -> None:
        super().__init__(node_1, node_2, delay_function)
        self.nodes = sorted([node_1, node_2], key=lambda node: node.address)
        self._delay_function = delay_function

    def get_destination(self, origin_address: str) -> SimulationNode:
        """Returns the destination node of the link from the origin address."""
        origin_node = None
        for node in self.nodes:
            if node.address == origin_address:
                origin_node = node
        if origin_node is None:
            raise Exception('Node is not part of the link.')
        destination_node = (set(self.nodes) - {origin_node}).pop()
        return destination_node


def convert_to_simulation_links(links: Iterable[Link],
                                simulation_nodes: Iterable[SimulationNode]) \
        -> Iterable[SimulationLink]:
    """Returns simulation links from regular links."""
    simulation_links = []
    for link in links:
        node_1, node_2 = get_equivalent_simulation_node(link.nodes,
                                                        simulation_nodes)
        # noinspection PyProtectedMember
        simulation_link = \
            SimulationLink(node_1, node_2, link._delay_function)
        simulation_links.append(simulation_link)
    return simulation_links


def get_all_links_of_node(node_address: str, links: Iterable[SimulationLink]) \
        -> Iterable[SimulationLink]:
    """Returns all the links of a node."""
    node_links = []
    for link in links:
        link_addresses = {node.address for node in link.nodes}
        if node_address in link_addresses:
            node_links.append(link)
    return node_links


def get_link_between_nodes(node1_address: str, node2_address: str,
                           links: Iterable[SimulationLink]) -> SimulationLink:
    """Returns the link between two nodes."""
    for link in links:
        link_node_addresses = {node.address for node in link.nodes}
        if link_node_addresses == {node1_address, node2_address}:
            return link
    raise Exception(f"Link between node {node1_address} and "
                    f"node {node2_address} does not exist.")
