"""Everything related with the network."""

from ..auxiliary_functions import print_with_asterisks


class Network:
    """Object that represent a Wireless Sensor Network."""

    def __init__(self, nodes, links):
        self.nodes = sorted(nodes, key=lambda node: node.address)
        self.links = links

    @print_with_asterisks
    def display_summary(self):
        """Shows a description of the network."""
        print('>> Network summary')
        print('> Nodes [node address, node name]:')
        for node in self.nodes:
            print(node)
        print()
        print('> Links [address node 1, address node 2]:')
        for link in self.links:
            print(link)
