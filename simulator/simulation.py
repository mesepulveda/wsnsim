"""Simulation related code."""
import random
import simpy

from simulator.link import convert_to_simulation_links
from simulator.medium import Medium
from simulator.network import SimulationNetwork
from simulator.node import convert_to_simulation_nodes

DEFAULT_SEED = 290696


class Simulation:
    """Manage a simulation."""

    def __init__(self, network, routing_protocol):
        self.env = simpy.Environment()
        self.medium = Medium(self.env)
        send_data_function = self.medium.send_data_to_medium
        simulation_nodes = convert_to_simulation_nodes(network.nodes,
                                                       routing_protocol,
                                                       send_data_function,
                                                       self.env)
        simulation_links = convert_to_simulation_links(network.links,
                                                       simulation_nodes)
        self.medium.setup_links(simulation_links)
        self.network = SimulationNetwork(simulation_nodes, simulation_links)

    def run(self, time, seed_value=DEFAULT_SEED):
        """Runs the simulation for a given time in seconds."""
        random.seed(seed_value)  # Restart the seed
        self.env.run(until=time)
