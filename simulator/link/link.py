"""Everything related with the simulation of a link."""
from simulator.auxiliary_functions import ensure_positive_value


class Link:
    """Relates two nodes in a physical medium."""

    def __init__(self, node_1, node_2, delay_function):
        self.nodes = sorted([node_1, node_2], key=lambda node: node.address)
        self._delay_function = delay_function

    @ensure_positive_value
    def get_delay(self):
        """Returns a realization of delay value of the link."""
        return self._delay_function()

    def __repr__(self):
        return '{0}, {1}'.format(*[node.address for node in self.nodes])

    def __str__(self):
        return '{0}, {1}'.format(*[node.address for node in self.nodes])


class SimulationLink(Link):
    """Extends Link class in order to simulate."""

    def __init__(self, node_1, node_2, delay_function):
        super().__init__(node_1, node_2, delay_function)


def convert_to_simulation_links(links):
    """Returns simulation links from regular links."""
    # noinspection PyProtectedMember
    simulation_links = [
        SimulationLink(*link.nodes, link._delay_function) for link in links
    ]
    return simulation_links
