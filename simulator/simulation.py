"""Simulation related code."""
from simulator.link import convert_to_simulation_links
from simulator.network import SimulationNetwork
from simulator.node import convert_to_simulation_nodes


class Simulation:
    """Manage a simulation."""
    def __init__(self, network):
        simulation_nodes = convert_to_simulation_nodes(network.nodes)
        simulation_links = convert_to_simulation_links(network.links)
        self.network = SimulationNetwork(simulation_nodes, simulation_links)

    def run(self, time):
        """Runs the simulation for a given time in seconds."""
        pass
