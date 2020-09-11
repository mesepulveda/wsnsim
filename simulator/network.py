"""Everything related with the network."""

from typing import Iterable

from .auxiliary_functions import print_with_asterisks
from .node import Node, SimulationNode
from .link import Link, SimulationLink


class Network:
    """Object that represent a Wireless Sensor Network."""

    def __init__(self, nodes: Iterable[Node], links: Iterable[Link]) -> None:
        self.nodes = sorted(nodes, key=lambda node: node.address)
        self.links = links

    @print_with_asterisks
    def display_summary(self) -> None:
        """Shows a description of the network."""
        print('>> Network summary')
        print('> Nodes [node address, node name]:')
        for node in self.nodes:
            print(node)
        print()
        print('> Links [address node 1, address node 2]:')
        for link in self.links:
            print(link)


class SimulationNetwork(Network):
    """Extends Network class in order to simulate."""

    def __init__(self,
                 simulation_nodes: Iterable[SimulationNode],
                 simulation_links: Iterable[SimulationLink]):
        super().__init__(simulation_nodes, simulation_links)
