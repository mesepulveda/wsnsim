"""Some functions that are useful in other files."""
from decimal import Decimal
from typing import Callable, Iterable


def print_with_asterisks(function: Callable[..., None]) -> Callable[..., None]:
    """Used as a decorator.

    Adds asterisks before and after the execution of a function.
    """
    def inner(*args, **kwargs):
        """Adds asterisks before and after the execution of a function."""
        number_of_asterisks = 50
        print('*' * number_of_asterisks)
        function(*args, **kwargs)
        print('*' * number_of_asterisks)

    return inner


def ensure_positive_value(function: Callable[..., float]) \
        -> Callable[..., float]:
    """Used as a decorator.

    Ensures that the value is 0 or positive.
    """
    def inner(*args, **kwargs):
        """Ensures that the value is 0 or positive."""
        value = function(*args, **kwargs)
        if value < 0:
            raise ValueError('Value obtained is negative')
        return value
    return inner


def get_components_of_message(data: str) -> Iterable[str]:
    """Returns the three components (origin, destination, message) of a data packet."""
    data_list = data.split(',')
    origin, destination, message = data_list
    return origin, destination, message


def is_hello_message(message: str) -> bool:
    """Checks if a message is a hello message."""
    if "Hello" in message:
        return True
    return False


def parse_payload(payload: str) -> Iterable[str]:
    """Parses the payload and returns the three components."""
    payload_components = payload.split('/')
    source, measurement, measurement_time = payload_components
    return source, measurement, float(measurement_time)


def float_range(start: float, stop: float, step: float) -> Iterable:
    """Float alternative for range()"""
    while start < stop:
        yield float(start)
        start += Decimal(step)


def is_etx_message(message: str) -> bool:
    """Checks if a message contains information about some neighbour ETX."""
    if "ETX" in message:
        return True
    return False


def divide_vector(vector: list, number: float) -> list:
    """Divides a vector."""
    divided_vector = [value / number for value in vector]
    return divided_vector


def multiply_vector(vector: list, number: float) -> list:
    """Multiply a vector."""
    multiplied_vector = [value * number for value in vector]
    return multiplied_vector


def find_index_of_delay(sample: float, delay_vector: list) -> int:
    """Returns the corresponding index for a new sample of the delay pdf."""
    for index, delay_value in enumerate(delay_vector):
        if sample <= delay_value:
            return index


def is_dap_message(message: str) -> bool:
    """Checks if a message contains information about some neighbour DAP."""
    if "DAP" in message:
        return True
    return False
