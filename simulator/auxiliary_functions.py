"""Some functions that might be useful in other files."""


def print_with_asterisks(function):
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


def ensure_positive_value(function):
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


def get_components_of_message(data):
    """Returns the three components (origin, destination, message)
    of a data packet."""
    data_list = data.split(',')
    origin = data_list[0]
    destination = data_list[1]
    message = data_list[2]
    return origin, destination, message
