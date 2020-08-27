"""Implements min-hop routing protocol/metric."""


def _find_min_hop_neighbour(neighbours):
    # todo: complete it properly
    if neighbours:
        return neighbours[0]


def _send_data_to_medium(data):
    """Sends the data to the medium in order to reach other nodes."""
    print(data)
    return True


class _MinHopRouting:
    """Private base class for the min-hop routing."""

    def __init__(self, address):
        self.address = address
        self.neighbours = set()
        self._find_neighbours()

    def send_message(self, message, destination):
        """Method to send a message to a destination."""
        next_hop = self._choose_next_hop(destination)
        return _send_data_to_medium(str(next_hop.address)+message)

    def _choose_next_hop(self, destination):
        """Returns one or a list of nodes to route data."""
        if destination == 'broadcast':
            return self.neighbours
        elif destination in self.neighbours:
            return destination
        if destination == 'sink':
            min_hop_neighbour = _find_min_hop_neighbour(self.neighbours)
            return min_hop_neighbour
        return None

    def _find_neighbours(self):
        """Method to discover neighbours."""
        # send 'hello'
        _send_data_to_medium('{},{},{}'.format(self.address, '', 'hello'))
        # wait until the neighbours answer...


class MinHopRouting(_MinHopRouting):
    """Class of min-hop routing protocol for sensing nodes."""

    def __init__(self, address):
        super().__init__(address)


class MinHopRoutingSink(_MinHopRouting):
    """Class of min-hop routing protocol for sink node."""

    def __init__(self, address):
        super().__init__(address)
