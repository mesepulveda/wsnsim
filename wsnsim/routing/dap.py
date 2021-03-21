"""Implements Deadline Achievement Probability (DAP) routing protocol/metric.

DAP:

1) Every node has a default end-to-end delay pdf.
2) Every node calculates link delay pdf with its neighbours.
3) A sharing phase start calculating DAP through every neighbour and updating
the own DAP to max(DAP | next-hop = u_i) and sharing again...
"""

from typing import Callable, Generator, Any, Optional, Dict
from random import choice

from simpy import Environment, Event

from .base_routing_protocol import RoutingProtocol
from ..auxiliary_functions import get_components_of_message, is_hello_message, parse_payload, float_range

DEADLINE = 20

PDF_AND_DAP_RESOLUTION = 1  # In seconds
PDF_AND_DAP_DURATION = 30  # In seconds


def divide_vector(vector: list, number: float):
    """Divides a vector."""
    divided_vector = [value / number for value in vector]
    return divided_vector


def multiply_vector(vector: list, number: float):
    """Multiply a vector."""
    multiplied_vector = [value * number for value in vector]
    return multiplied_vector


class DelayPDF:
    """Delay PDF object."""

    def __init__(self):
        self.delay_vector = list(float_range(0, PDF_AND_DAP_DURATION, PDF_AND_DAP_RESOLUTION)) + [float('inf')]
        self.delay_pdf_vector = [0] * len(self.delay_vector)
        self._number_of_samples = 0

    def update_with_new_sample(self, sample: float):
        """Updates the delay pdf information with a new sample."""
        old_number_of_samples = self._number_of_samples
        self._number_of_samples += 1
        index = find_index_of_delay(sample, self.delay_vector)
        if self._number_of_samples == 1:
            self.delay_pdf_vector[index] = 1
            return
        denormalized_pdf = multiply_vector(self.delay_pdf_vector, old_number_of_samples)
        denormalized_pdf[index] += 1
        self.delay_pdf_vector = divide_vector(denormalized_pdf, self._number_of_samples)

    def __len__(self):
        return len(self.delay_vector)

    def __repr__(self):
        return str(self.delay_pdf_vector)

    __str__ = __repr__


class DAP:
    """DAP object."""

    def __init__(self, dap_vector: list = None, sink: bool = False):
        self.deadline_vector = list(float_range(0, PDF_AND_DAP_DURATION, PDF_AND_DAP_RESOLUTION)) + [float('inf')]
        if dap_vector:
            self.dap_vector = dap_vector
        else:
            if sink:
                self.dap_vector = [1] * len(self.deadline_vector)
            else:
                self.dap_vector = [0] * len(self.deadline_vector)


    def get_dap(self, deadline: float) -> float:
        """Returns the DAP for a given deadline."""
        if deadline <= 0:
            return 0
        index = find_index_of_delay(deadline, self.deadline_vector)
        return self.dap_vector[index]

    def vector_to_text(self) -> str:
        """"Returns the text version of the DAP vector."""
        return str(self.dap_vector).replace(',', '|')

    def __len__(self):
        return len(self.deadline_vector)

    def __repr__(self):
        return str(self.dap_vector)

    __str__ = __repr__


class Neighbour:
    """Definition of a neighbour in the context of DAP routing."""

    def __init__(self, address: str):
        self.address = address
        self.link_delay_pdf = DelayPDF()
        self.dap = DAP()
        self.dap_through_neighbour = DAP()

    def update_link_delay_pdf(self, sample: float) -> None:
        """Updates the delay pdf with a new delay sample."""
        self.link_delay_pdf.update_with_new_sample(sample)

    def update_dap(self, new_dap: str) -> None:
        """Updates the neighbour DAP."""
        new_dap = new_dap.strip('[]').split('|')
        new_dap = [float(dap) for dap in new_dap]
        self.dap = DAP(new_dap)
        self.update_dap_through_neighbour()

    def update_dap_through_neighbour(self) -> None:
        """Updates the DAP though neighbour"""
        self.dap_through_neighbour = convolution_of_dap_with_delay_pdf(self.dap, self.link_delay_pdf)

    def get_dap_through_neighbour(self, deadline: float) -> float:
        """Returns the DAP through this neighbour for a given deadline."""
        return self.dap_through_neighbour.get_dap(deadline)

    def __repr__(self):
        return f'Address: {self.address}'

    def __str__(self):
        return f'Address: {self.address}'

    def __eq__(self, other):
        return other.address == self.address

    def __hash__(self):
        return hash(self.address)


def find_index_of_delay(sample: float, delay_vector: list):
    """Returns the corresponding index for a new sample of the delay pdf."""
    for index, delay_value in enumerate(delay_vector):
        if sample <= delay_value:
            return index


def convolution_of_dap_with_delay_pdf(dap: DAP, delay_pdf: DelayPDF) -> DAP:
    """Convolve a DAP with a DelayPDF in order to generate a new DAP."""
    dap_vector = dap.dap_vector
    dap_length = len(dap_vector)

    delay_vector = delay_pdf.delay_pdf_vector
    delay_length = len(delay_vector)

    assert dap_length == delay_length
    new_dap = [0]*dap_length

    for delay_index, delay_value in enumerate(delay_vector):
        for dap_index, dap_value in enumerate(dap_vector):
            new_dap_index = delay_index + dap_index
            new_dap_probability = delay_value*dap_value
            if new_dap_index < dap_length - 1:
                new_dap[new_dap_index] += new_dap_probability
            else:
                new_dap[-1] += new_dap_probability
    if new_dap[-1] > 1:
        new_dap[-1] = 1.0
    return DAP(new_dap)


class _DAPRouting(RoutingProtocol):
    """Implements methods used in DAP for both sink and sensing nodes."""
    _neighbours: Dict[str, Neighbour]
    deadline = DEADLINE
    dap_share_period = 60*60  # Time between messages sharing the own DAP

    def __init__(self,
                 address: str,
                 radio: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, radio, env)
        self._neighbours = dict()

    def add_to_output_queue(self, message: str, destination: str) \
            -> Generator[Event, Any, Any]:
        """Adds a message to the output queue."""
        self._log_output_queue_message(message, destination)
        with self._output_queue.request() as req:
            yield req
            yield self.env.process(self._send_packet(message, destination))

    def _send_packet(self, message: str, destination: str) \
            -> Generator[Event, Any, Any]:
        """Method to send a message to a destination."""
        prove_packet = destination not in ['', 'broadcast', 'sink']
        if is_hello_message(message) or is_dap_message(message):
            measurement_time = 0
        else:
            _, _, measurement_time = parse_payload(message)
        time_to_deadline = self.deadline - (self.env.now - measurement_time)
        next_hop_address = self._choose_next_hop_address(destination, time_to_deadline)
        if next_hop_address is None:
            raise Exception('No next hop address was returned to route·')
        data = '{},{},{}'.format(self.address, next_hop_address, message)
        self._print_info(f'sending: {data[:200]}')
        self._log_message_sending(data, destination)
        if prove_packet:
            start_time = self.env.now
            yield self.env.process(self._radio(data))
            end_time = self.env.now
            delay = end_time - start_time
            self._neighbours[destination].update_link_delay_pdf(delay)
        else:
            yield self.env.process(self._radio(data))
        self._log_message_sent(data, destination)

    def _analyze_hello_message(self, origin_address: str) -> None:
        """Checks information of Hello message."""
        new_neighbour = Neighbour(origin_address)
        if new_neighbour.address not in self._neighbours:
            self._neighbours[new_neighbour.address] = new_neighbour
            self.env.process(self.add_to_output_queue(f'Hello', 'broadcast'))

    def _choose_next_hop_address(self, destination: str, time_to_deadline: float) -> Optional[str]:
        """Returns one nodes to route data."""
        if destination == 'broadcast' or destination == '':
            return ''
        elif destination in self._neighbours:
            return destination
        elif destination == 'sink':
            max_dap_address = _find_max_dap_neighbour(self._neighbours, time_to_deadline)
            return max_dap_address
        return None


def _find_max_dap_neighbour(neighbours_dict: Dict[str, Neighbour], time_to_deadline: float) -> str:
    """Returns the address of the selected forwarder with minimum Max DAP toward the sink."""
    neighbours = neighbours_dict.values()
    max_dap_through_neighbour = max({neighbour.get_dap_through_neighbour(time_to_deadline) for neighbour in neighbours})
    # '<=' added instead of '==' for floating point arithmetic compatibility
    max_dap_neighbours = [n for n in neighbours if
                          n.get_dap_through_neighbour(time_to_deadline) >= max_dap_through_neighbour]
    neighbour_selected = choice(max_dap_neighbours)
    return neighbour_selected.address


class DAPRouting(_DAPRouting):
    """Class of DAP routing protocol for sensing nodes."""

    probe_packet_rate = 1  # Per neighbour per hour

    def __init__(self,
                 address: str,
                 radio: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, radio, env)
        self.dap = DAP()

    def active_link_probing(self) -> Generator[Event, Any, Any]:
        """Routine to actively probe the links with dummy packets."""
        yield self.env.timeout(1)
        probe_per_hour = self.probe_packet_rate*len(self._neighbours)
        probe_period = 60*60/probe_per_hour
        message = "DAP+dummy"
        # Fist probe to every neighbour
        for address in self._neighbours:
            self.env.process(self.add_to_output_queue(message, address))
        # Probes are sent periodically
        while True:
            for address, neighbour in self._neighbours.items():
                yield self.env.timeout(probe_period)
                self.env.process(self.add_to_output_queue(message, address))

    def update_dap(self) -> None:
        """Updates the own DAP."""
        neighbours = self._neighbours.values()
        for index in range(len(self.dap)):
            dap_through_neighbours = {neighbour.dap_through_neighbour.dap_vector[index]
                                      for neighbour in neighbours}
            self.dap.dap_vector[index] = max(dap_through_neighbours)

    def share_dap(self) -> Generator[Event, Any, Any]:
        """Routine to share the own DAP periodically."""
        yield self.env.timeout(60)  # wait for a minute before share the DAP
        while True:
            self.update_dap()
            message = f"DAP+{self.dap.vector_to_text()}"
            self.env.process(self.add_to_output_queue(message, "broadcast"))
            yield self.env.timeout(self.dap_share_period)

    def setup(self) -> Generator[Event, Any, Any]:
        """Initiates the neighbours discovery with hop count."""
        self.env.process(self.share_dap())
        self.env.process(self.active_link_probing())
        # noinspection PyArgumentEqualDefault
        yield self.env.timeout(0)

    def receive_packet(self, message: str) -> None:
        """Method called when a packet arrives."""
        self._log_received_message(message)
        self._print_info(f'received: {message[:200]}')
        origin_address, destination_address, info = \
            get_components_of_message(message)
        assert destination_address == self.address or destination_address == ''
        if is_hello_message(info):
            # It is a hello message
            self._analyze_hello_message(origin_address)
        elif is_dap_message(info):
            # It is a dap message
            self._analyze_dap_message(origin_address, info)
        else:
            # It is not a hello message, so it should be forwarded
            self.env.process(self.add_to_output_queue(info, 'sink'))
            return

    def _analyze_dap_message(self, origin_address: str, info: str) -> None:
        """Updates the neighbour information with a new DAP or discard if it is
         a dummy packet."""
        if "dummy" not in info:
            new_dap = info.split('+')[1]
            self._neighbours[origin_address].update_dap(new_dap)


def is_dap_message(message: str) -> bool:
    """Checks if a message contains information about some neighbour DAP."""
    if "DAP" in message:
        return True
    return False


class DAPRoutingSink(_DAPRouting):
    """Class of DAP routing protocol for sink node."""

    def __init__(self,
                 address: str,
                 radio: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        super().__init__(address, radio, env)
        self.dap = DAP(sink=True)

    def share_dap(self) -> Generator[Event, Any, Any]:
        """Routine to share the own DAP periodically."""
        while True:
            message = f"DAP+{self.dap.vector_to_text()}"
            self.env.process(self.add_to_output_queue(message, "broadcast"))
            yield self.env.timeout(self.dap_share_period)

    def setup(self) -> None:
        """Initiates the neighbours discovery with hop count."""
        yield self.env.process(self.add_to_output_queue(f'Hello', 'broadcast'))
        self.env.process(self.share_dap())

    def receive_packet(self, message: str) -> None:
        """Method called when a packet arrives."""
        self._log_received_message(message)
        self._print_info(f'received: {message[:200]}')
        origin_address, destination_address, info = \
            get_components_of_message(message)
        assert destination_address == self.address or destination_address == ''
        if is_hello_message(info):
            # It is a hello message
            self._analyze_hello_message(origin_address)
        elif is_dap_message(info):
            # It is a DAP message the sink does nothing
            pass
        else:
            # It is not a hello message, so it reached the sink node
            self._print_info(f'message: {info} reached sink node')
