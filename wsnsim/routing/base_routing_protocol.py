"""This module implements a base structure for every routing protocol."""

from typing import Callable, Generator, Any

from simpy import Event, Environment, Resource


class RoutingProtocol:
    """Base class for every routing protocol."""

    def __init__(self,
                 address: str,
                 radio: Callable[[str], Generator[Event, Any, Any]],
                 env: Environment) -> None:
        self.address = address
        self._radio = radio
        self.env = env
        # noinspection PyArgumentEqualDefault
        # 'capacity' sets the quantity of packets that can be sent at the same time
        # 'capacity=1' sets a more realistic model with queue delay for congested networks
        # 'capacity=9999999' sets a less realistic model without queue delay for congested networks
        self._output_queue = Resource(env, capacity=1)
        # List to save messages in format: (timestamp, message)
        # Used to calculate performance
        self._received_messages = []
        self._output_queue_messages = []
        self._message_sending = []
        self._message_sent = []

    def setup(self) -> Generator[Event, Any, Any]:
        """Any setup code must go here."""
        pass

    def receive_packet(self, message: str) -> Generator[Event, Any, Any]:
        """Method called when a packet arrives."""
        pass

    def add_to_output_queue(self, message: str, destination: str) -> Generator[Event, Any, Any]:
        """Adds a message to the output queue."""
        pass

    def _print_info(self, info: str, limit: int = 200) -> None:
        """Prints information with format."""
        print(f'{self.env.now:.2f} | {self.address} | {info[:limit]}')

    def _log_received_message(self, message: str) -> None:
        """Logs the timestamp when a message is received."""
        self._received_messages.append((self.env.now, message))

    def _log_output_queue_message(self, message: str, destination: str) -> None:
        """Logs the timestamp when a message arrives to output queue."""
        self._output_queue_messages.append((self.env.now,
                                            message,
                                            destination))

    def _log_message_sending(self, message: str, destination: str) -> None:
        """Logs the timestamp when a message was sent."""
        self._message_sending.append((self.env.now, message, destination))

    def _log_message_sent(self, message: str, destination: str) -> None:
        """Logs the timestamp when a message was sent."""
        self._message_sent.append((self.env.now, message, destination))
