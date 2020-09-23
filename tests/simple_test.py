"""Some very simple test of the simulator."""

from wsnsim import SinkNode, SensingNode, Link, Network, Simulation


def test_1():
    # Create two nodes
    sink = SinkNode('0', 'sink')
    sensing = SensingNode('1')
    # Create one link
    link = Link(sink, sensing, lambda: 5)
    # Create network
    network = Network({sink, sensing}, {link})
    # Show information about the network
    network.display_summary()
    # Create simulation
    simulation = Simulation(network, routing_protocol='min-hop')
    # Run it
    simulation.run(60)  # Time in seconds


if __name__ == '__main__':
    test_1()
