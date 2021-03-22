"""Some very simple test of the simulator."""

from wsnsim import SinkNode, SensingNode, Link, Network, Simulation


def test_1():
    """
          (2)
         1 - 3
     (1)/    |(3)
     0 - 2 - 4 - 5
      (4) (5) (6)
    """
    # Create nodes
    sink = SinkNode('0', name='sink')
    sensing_1 = SensingNode('1', sensing_period=60*60, sensing_offset=10*60)
    sensing_2 = SensingNode('2', sensing_period=60*60, sensing_offset=20*60)
    sensing_3 = SensingNode('3', sensing_period=60*60, sensing_offset=30*60)
    sensing_4 = SensingNode('4', sensing_period=60*60, sensing_offset=40*60)
    sensing_5 = SensingNode('5', sensing_period=60*60, sensing_offset=50*60)
    # Create links
    link_1 = Link(sink, sensing_1, lambda: 1)
    link_2 = Link(sensing_1, sensing_3, lambda: 2)
    link_3 = Link(sensing_3, sensing_4, lambda: 3)
    link_4 = Link(sink, sensing_2, lambda: 4)
    link_5 = Link(sensing_2, sensing_4, lambda: 5)
    link_6 = Link(sensing_4, sensing_5, lambda: 6)
    # Create network
    network = Network({sink,
                       sensing_1,
                       sensing_2,
                       sensing_3,
                       sensing_4,
                       sensing_5},
                      {link_1, link_2, link_3, link_4, link_5, link_6})
    # Show information about the network
    network.display_summary()
    # Create simulation
    routing_protocol = 'etx'  # min-hop, etx or dap
    deadline = 20  # In seconds
    simulation = Simulation(network, routing_protocol, deadline)
    # Run it
    simulation.run(30*24*60*60)  # Time in seconds
    # Show the performance
    simulation.show_performance()


if __name__ == '__main__':
    test_1()
