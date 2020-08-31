"""Simulation related code."""
import random

from simulator.link import convert_to_simulation_links
from simulator.medium import Medium, setup_nodes_medium_access
from simulator.network import SimulationNetwork
from simulator.node import convert_to_simulation_nodes

DEFAULT_SEED = 290696


class Simulation:
    """Manage a simulation."""

    def __init__(self, network, protocol_stack):
        self.protocol_stack = protocol_stack
        if self.protocol_stack == 'default':
            routing_stack = 'min-hop'
        simulation_nodes = convert_to_simulation_nodes(network.nodes,
                                                       routing_stack)
        simulation_links = convert_to_simulation_links(network.links,
                                                       simulation_nodes)
        self.medium = Medium(simulation_links)
        setup_nodes_medium_access(simulation_nodes,
                                  self.medium.send_data_to_medium)
        self.network = SimulationNetwork(simulation_nodes, simulation_links)

    def run(self, time, seed_value=DEFAULT_SEED):
        """Runs the simulation for a given time in seconds."""
        self.clean_simulation(seed_value)
        pass

    def clear_simulation(self, seed_value=None):
        """Clears everything before a simulation is run."""
        # Clear logging variables of network, nodes and links
        self.network.clear_simulation()
        for node in self.network.nodes:
            node.clear_simulation()
        for link in self.network.links:
            link.clear_simulation()
        # Restart the seed
        if seed_value:
            random.seed(seed_value)
