"""Some very simple test of the simulator."""

from simulator.node import SinkNode, SensingNode
from simulator.link import Link
from simulator.network import Network


def test_1():
    # Create two nodes
    sink = SinkNode(0, 'sink')
    sensing = SensingNode(1, 'node 1')
    # Create one link
    link = Link(sink, sensing)
    # Create network
    network = Network({sink, sensing}, {link})
    # Show information about the network
    network.display_summary()


if __name__ == '__main__':
    test_1()
