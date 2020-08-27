"""Everything related with the simulation of a link."""
from simulator.auxiliary_functions import ensure_positive_value


class Link:
    """Relates two nodes in a physical medium."""
    def __init__(self, node_1, node_2, delay_function, **kwargs):
        self.nodes = sorted([node_1, node_2], key=lambda node: node.address)
        self._delay_function = delay_function
        for key, value in kwargs.items():
            setattr(self, key, value)

    @ensure_positive_value
    def get_delay(self):
        """Returns a realization of delay value of the link."""
        return self.delay_function()

    def __repr__(self):
        return '{0}, {1}'.format(*[node.address for node in self.nodes])

    def __str__(self):
        return '{0}, {1}'.format(*[node.address for node in self.nodes])


