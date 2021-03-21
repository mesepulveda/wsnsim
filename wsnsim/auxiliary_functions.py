"""Some functions that might be useful in other files."""
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
    """Returns the three components (origin, destination, message)
    of a data packet."""
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


def float_range(start: float, stop: float, step: float):
    """Float alternative for range()"""
    while start < stop:
        yield float(start)
        start += Decimal(step)