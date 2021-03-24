""" Test with the network presented in Sepulveda2021a 'On the Deadline Miss Probability of Various Routing Policies in
Wireless Sensor Networks'."""

from scipy.stats import gamma

from wsnsim import SinkNode, SensingNode, Link, Network, Simulation


def test_1():
    """
    Topology:

     --------------
    |    -------- |
    |   |       |/
    1 - 2 - 3 - 0
            |   |
            4 --

    """
    # Create nodes
    sink = SinkNode('0', name='sink')
    sensing_1 = SensingNode('1', sensing_period=60 * 60, sensing_offset=15 * 60)
    sensing_2 = SensingNode('2', sensing_period=60 * 60, sensing_offset=30 * 60)
    sensing_3 = SensingNode('3', sensing_period=60 * 60, sensing_offset=45 * 60)
    sensing_4 = SensingNode('4', sensing_period=60 * 60, sensing_offset=60 * 60)
    # Create links
    alpha_1s, beta_1s = 10, 0.25
    alpha_12, beta_12 = 25, 5
    alpha_2s, beta_2s = 1.15, 0.08
    alpha_23, beta_23 = 5, 1
    alpha_3s, beta_3s = 16, 2
    alpha_34, beta_34 = 1.11, 0.44
    alpha_4s, beta_4s = 1.03, 0.25
    # Delays are random variables with a Gamma distribution as PDF
    link_10 = Link(sensing_1, sink, lambda: gamma.rvs(alpha_1s, scale=1/beta_1s, size=1)[0])
    link_20 = Link(sensing_2, sink, lambda: gamma.rvs(alpha_2s, scale=1/beta_2s, size=1)[0])
    link_30 = Link(sensing_3, sink, lambda: gamma.rvs(alpha_3s, scale=1/beta_3s, size=1)[0])
    link_40 = Link(sensing_4, sink, lambda: gamma.rvs(alpha_4s, scale=1/beta_4s, size=1)[0])
    link_12 = Link(sensing_1, sensing_2, lambda: gamma.rvs(alpha_12, scale=1/beta_12, size=1)[0])
    link_23 = Link(sensing_2, sensing_3, lambda: gamma.rvs(alpha_23, scale=1/beta_23, size=1)[0])
    link_34 = Link(sensing_3, sensing_4, lambda: gamma.rvs(alpha_34, scale=1/beta_34, size=1)[0])
    # Create network
    nodes = {sink, sensing_1, sensing_2, sensing_3, sensing_4}
    links = {link_10, link_20, link_30, link_40, link_12, link_23, link_34}
    network = Network(nodes, links)
    # Show information about the network
    network.display_summary()
    # Create simulation
    routing_protocol = 'min-hop'  # min-hop, etx or dap
    deadline = 24  # In seconds
    simulation = Simulation(network, routing_protocol, deadline)
    # Run the simulation
    simulation.run(30*24*60*60)  # Time in seconds
    # Show the performance
    simulation.show_performance()


if __name__ == '__main__':
    test_1()
