"""Implements min-hop routing protocol/metric."""
from simulator.auxiliary_functions import get_components_of_message


def _find_min_hop_neighbour(neighbours):
    # todo: complete it properly
    if neighbours:
        return neighbours[0]


class _MinHopRouting:
    """Private base class for the min-hop routing."""

    def __init__(self, address):
        self.address = address
        self.neighbours = set()
        self.access_function = None

    def _send_data_to_medium(self, data):
        return self.access_function(data)

    def send_message(self, message, destination):
        """Method to send a message to a destination."""
        next_hop_address = self._choose_next_hop_address(destination)
        if next_hop_address is None:
            # First we need to discover neighbours
            self._find_neighbours()
            return self.send_message(message, destination)
        data = '{},{},{}'.format(self.address, next_hop_address, message)
        print('{0} sending: {1}'.format(self.address, data))
        self._send_data_to_medium(data)

    def receive_message(self, message):
        print('{0} received: {1}'.format(self.address, message))
        origin_address, _, data = get_components_of_message(message)
        self.neighbours.add(origin_address)
        if data != 'ACK':
            self.send_message('ACK', origin_address)

    def _choose_next_hop_address(self, destination):
        """Returns one or a list of nodes to route data."""
        if destination == 'broadcast':
            return ''
        elif destination in self.neighbours:
            return destination
        elif destination == 'sink':
            min_hop_neighbour = _find_min_hop_neighbour(self.neighbours)
            return min_hop_neighbour.address
        return None

    def _find_neighbours(self):
        """Method to discover neighbours."""
        # send 'hello'
        self._send_data_to_medium('{},{},{}'.format(self.address, '', 'hello'))
        # wait until the neighbours answer...


class MinHopRouting(_MinHopRouting):
    """Class of min-hop routing protocol for sensing nodes."""

    def __init__(self, address):
        super().__init__(address)


class MinHopRoutingSink(_MinHopRouting):
    """Class of min-hop routing protocol for sink node."""

    def __init__(self, address):
        super().__init__(address)
