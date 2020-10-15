"""A simple test to check the behavior with pdfs."""
from random import uniform

from wsnsim import SinkNode, SensingNode, Link, Network, Simulation


def test_1():
    """
    0 - 1 - 2
    """
    # Create nodes
    sink = SinkNode('0', name='sink')
    sensing_1 = SensingNode('1', sensing_period=60*60, sensing_offset=15*60)
    sensing_2 = SensingNode('2', sensing_period=60*60, sensing_offset=45*60)
    # Create links
    link_1 = Link(sink, sensing_1, lambda: uniform(5, 10))
    link_2 = Link(sensing_1, sensing_2, lambda: uniform(5, 10))
    # Create network
    network = Network({sink,
                       sensing_1,
                       sensing_2,},
                      {link_1, link_2})
    # Show information about the network
    network.display_summary()
    # Create simulation
    simulation = Simulation(network, routing_protocol='etx')
    # Run it
    simulation.run(365*24*60*60)  # Time in seconds
    # Show the performance
    simulation.show_performance()


if __name__ == '__main__':
    test_1()
