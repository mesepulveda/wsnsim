"""Test for a network with 3 nodes and random delays."""

from random import uniform

from wsnsim import SinkNode, SensingNode, Link, Network, Simulation


def test_1():
    """
    Topology:

    0 - 1 - 2

    """
    # Create nodes
    sink = SinkNode('0', name='sink')
    sensing_1 = SensingNode('1', sensing_period=60*60, sensing_offset=15*60)
    sensing_2 = SensingNode('2', sensing_period=60*60, sensing_offset=45*60)
    # Create links
    link_1 = Link(sink, sensing_1, lambda: uniform(5, 10))       # Delay is a random variable with a PDF
    link_2 = Link(sensing_1, sensing_2, lambda: uniform(5, 10))  # Delay is a random variable with a PDF
    # Create network
    nodes = {sink, sensing_1, sensing_2}
    links = {link_1, link_2}
    network = Network(nodes, links)
    # Show information about the network
    network.display_summary()
    # Create simulation
    routing_protocol = 'etx'  # min-hop, etx or dap
    deadline = 20  # In seconds
    simulation = Simulation(network, routing_protocol, deadline)
    # Run the simulation
    simulation.run(365*24*60*60)  # Time in seconds
    # Show the performance
    simulation.show_performance()


if __name__ == '__main__':
    test_1()
