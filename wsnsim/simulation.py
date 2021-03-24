"""Simulation related code."""

from random import seed

from simpy import Environment

from .link import convert_to_simulation_links
from .medium import Medium

from .network import Network, SimulationNetwork
from .node import convert_to_simulation_nodes
from .performance import NetworkPerformance

DEFAULT_SEED = 290696


class Simulation:
    """Manage a simulation."""

    def __init__(self, network: Network, routing_protocol: str, deadline: float) -> None:
        self.env = Environment()
        self.medium = Medium(self.env)
        send_data_function = self.medium.send_data_to_medium
        simulation_nodes = convert_to_simulation_nodes(network.nodes,
                                                       routing_protocol,
                                                       deadline,
                                                       send_data_function,
                                                       self.env)
        simulation_links = convert_to_simulation_links(network.links, simulation_nodes)
        self.medium.setup_links(simulation_links)
        self.network = SimulationNetwork(simulation_nodes, simulation_links)
        self.deadline = deadline

    def run(self, time: float, seed_value: int = DEFAULT_SEED) -> None:
        """Runs the simulation for a given time in seconds."""
        seed(seed_value)  # Restart the seed
        self.env.run(until=time)

    def show_performance(self):
        """Calls a routine to show the performance of the simulation."""
        NetworkPerformance(self.network, self.deadline)
