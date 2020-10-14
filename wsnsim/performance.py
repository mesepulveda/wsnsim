"""Everything related with the calculation of performance goes here."""
from typing import Iterable, Tuple, List, Dict

import matplotlib.pyplot as plt

from .auxiliary_functions import get_components_of_message, is_hello_message, \
    parse_payload
from .network import SimulationNetwork
from .node import get_sink_node
from .routing.etx import is_etx_message


class NetworkPerformance:
    """Performs the calculations of the network performance."""

    def __init__(self, network: SimulationNetwork):
        self.nodes = network.nodes.copy()
        self.sink = get_sink_node(self.nodes)
        self.nodes.remove(self.sink)
        self.show_end_to_end_statistics()

    def calculate_end_to_end_delay_pdf(self) -> Dict:
        """Calculates the end to end delay pdf for every sensing node."""
        sink_received_messages = self.sink.routing_protocol._received_messages
        # Calculate the end to end delay
        end_to_end_list = get_end_to_end_delay_list(sink_received_messages)
        # Split the list for every sensing node
        end_to_end_dict = split_end_to_end_delay_list(end_to_end_list)
        return end_to_end_dict

    def show_end_to_end_statistics(self):
        """Plots the statistics."""
        end_to_end_delay = self.calculate_end_to_end_delay_pdf()
        for node, delay_list in end_to_end_delay.items():
            plt.figure()
            plt.hist(delay_list, density=True)
            plt.grid()
            plt.title(node)
            plt.show()


def get_end_to_end_delay_list(received_messages: Iterable[Tuple[float, str]]) \
        -> Iterable[Tuple[str, float]]:
    """Returns a list of (origin, delay) tuples from a sink received messages
    list."""

    end_to_end_list: List[Tuple[str, float]] = []
    for incoming_time, data in received_messages:
        _, _, message = get_components_of_message(data)
        if is_hello_message(message) or is_etx_message(message):
            continue
        source, _, measurement_time = parse_payload(message)
        delay = incoming_time - measurement_time
        end_to_end_list.append((source, delay))
    return end_to_end_list


def split_end_to_end_delay_list(end_to_end_list: Iterable[Tuple[str, float]]) \
        -> Dict:
    """Does something."""

    split_delay_dict = {}
    for node, delay in end_to_end_list:
        if node in split_delay_dict:
            split_delay_dict[node].append(delay)
        else:
            split_delay_dict[node] = [delay]
    return split_delay_dict
