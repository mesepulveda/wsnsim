"""Some functions that might be useful in other files."""


def add_asterisks(function):
    """Used as a decorator."""
    def inner(*args, **kwargs):
        """Adds asterisks before and after the execution of a function."""
        number_of_asterisks = 50
        print('*' * number_of_asterisks)
        function(*args, **kwargs)
        print('*' * number_of_asterisks)

    return inner
