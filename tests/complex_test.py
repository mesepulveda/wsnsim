"""Some very simple test of the simulator."""

from wsnsim import SinkNode, SensingNode, Link, Network, Simulation


def test_1():
    """
         1 - 3
       /     |
     0 - 2 - 4 - 5
    """
    # Create nodes
    sink = SinkNode('0', wakeup_offset=10, name='sink')
    sensing_1 = SensingNode('1', sensing_period=15*60, wakeup_offset=5)
    sensing_2 = SensingNode('2', sensing_period=15*60, wakeup_offset=5)
    sensing_3 = SensingNode('3', sensing_period=15*60, wakeup_offset=5)
    sensing_4 = SensingNode('4', sensing_period=15*60, wakeup_offset=5)
    sensing_5 = SensingNode('5', sensing_period=15*60, wakeup_offset=5)
    # Create links
    link_1 = Link(sink, sensing_1, lambda: 1)
    link_2 = Link(sink, sensing_2, lambda: 2)
    link_3 = Link(sensing_1, sensing_3, lambda: 3)
    link_4 = Link(sensing_2, sensing_4, lambda: 4)
    link_5 = Link(sensing_3, sensing_4, lambda: 5)
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
    simulation = Simulation(network, routing_protocol='min-hop')
    # Run it
    simulation.run(20*60)  # Time in seconds


if __name__ == '__main__':
    test_1()
