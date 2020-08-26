"""Everything related with the simulation of a link."""


class Link:
    """Relates two nodes in a physical medium."""
    def __init__(self, node_1, node_2):
        self.nodes = sorted([node_1, node_2], key=lambda node: node.address)

    def __repr__(self):
        return '{0}, {1}'.format(*[node.address for node in self.nodes])

    def __str__(self):
        return '{0}, {1}'.format(*[node.address for node in self.nodes])
