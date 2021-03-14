"""Implements Deadline Achievement Probability (DAP) routing protocol/metric.

DAP:

1) Every node has a default end-to-end delay pdf.
2) Every node calculates link delay pdf with its neighbours.
3) A sharing phase start calculating DAP through every neighbour and updating
the own DAP to max(DAP | next-hop = u_i) and sharing again...
"""

from typing import List, Callable, Generator, Any, Optional, Dict
from random import choice
from statistics import mean
from decimal import Decimal

from simpy import Environment, Event

from .base_routing_protocol import RoutingProtocol
from ..auxiliary_functions import get_components_of_message, is_hello_message

PDF_AND_DAP_RESOLUTION = 0.001  # In seconds
PDF_AND_DAP_DURATION = 60  # In seconds


class Vector(list):
    """Vector object."""

    def __init__(self, values: List):
        super().__init__()
        self.values = values

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            multiplied_vector = [value*other for value in self.values]
            return Vector(multiplied_vector)

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            divided_vector = [value/other for value in self.values]
            return Vector(divided_vector)


class DelayPDF:
    """Delay PDF object."""

    def __init__(self, resolution: float = PDF_AND_DAP_RESOLUTION, length: float = PDF_AND_DAP_DURATION):
        self._resolution = resolution
        self._length = length
        self.delay_vector = Vector([float_range(0, self._length, self._resolution)] + [float('inf')])
        self.delay_pdf = Vector([0] * len(self.delay_vector))
        self._number_of_samples = 0

    def update_with_new_sample(self, sample: float):
        """Updates the delay pdf information with a new sample."""
        old_number_of_samples = self._number_of_samples
        self._number_of_samples += 1
        index = find_index_of_new_sample(sample, self.delay_vector)
        if self._number_of_samples == 1:
            self.delay_vector[index] = 1
            return
        denormalized_pdf = self.delay_pdf * old_number_of_samples
        denormalized_pdf[index] += 1
        self.delay_pdf = denormalized_pdf/self._number_of_samples


class DAP:
    """DAP object."""

    def __init__(self, resolution: float = PDF_AND_DAP_RESOLUTION, length: float = PDF_AND_DAP_DURATION):
        self._resolution = resolution
        self._length = length
        self.deadline_vector = Vector([float_range(0, self._length, self._resolution)] + [float('inf')])


class Neighbour:
    """Definition of a neighbour in the context of DAP routing."""

    def __init__(self, address: str, link_delay_pdf: DelayPDF = DelayPDF(), dap: DAP = DAP(),
                 dap_through_neighbour: DAP = DAP()):
        self.address = address
        self.link_delay_pdf = link_delay_pdf
        self.dap = dap
        self.dap_through_neighbour = dap_through_neighbour


def float_range(start: float, stop: float, step: float):
    """Float alternative for range()"""
    while start < stop:
        yield float(start)
        start += Decimal(step)


def find_index_of_new_sample(sample: float, delay_vector: Vector):
    """Returns the corresponding index for a new sample of the delay pdf."""
    for index, delay_value in enumerate(delay_vector):
        if sample <= delay_value:
            return index
