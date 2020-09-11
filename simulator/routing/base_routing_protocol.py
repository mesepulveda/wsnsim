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
        self._output_queue = Resource(env, capacity=1)

    def receive_packet(self, message: str) -> Generator[Event, Any, Any]:
        """Method called when a packet arrives."""
        pass

    def add_to_output_queue(self, message: str, destination: str) \
            -> Generator[Event, Any, Any]:
        """Adds a message to the output queue."""
        pass

    def setup(self) -> Generator[Event, Any, Any]:
        """Any setup code must go here."""
        pass
