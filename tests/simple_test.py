"""Test of the simulator with 2 nodes and fixed delays."""

from wsnsim import SinkNode, SensingNode, Link, Network, Simulation


def test_1():
    """
    Topology:

      (5)
     0 - 1

    """
    # Create nodes
    sink = SinkNode('0', name='sink')
    sensing = SensingNode('1')
    # Create one link
    link = Link(sink, sensing, lambda: 5)  # 5 seconds delay
    # Create network
    nodes = {sink, sensing}
    links = {link}
    network = Network(nodes, links)
    # Show information about the network
    network.display_summary()
    # Create simulation
    routing_protocol = 'min-hop'  # min-hop, etx or dap
    deadline = 20  # In seconds
    simulation = Simulation(network, routing_protocol, deadline)
    # Run the simulation
    simulation.run(2*60)  # Time in seconds


if __name__ == '__main__':
    test_1()
