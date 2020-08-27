"""Everything related with the simulation of a link."""


class Link:
    """Relates two nodes in a physical medium."""
    def __init__(self, node_1, node_2, delay_function, **kwargs):
        self.nodes = sorted([node_1, node_2], key=lambda node: node.address)
        self.delay_function = ensure_positive_value(delay_function)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return '{0}, {1}'.format(*[node.address for node in self.nodes])

    def __str__(self):
        return '{0}, {1}'.format(*[node.address for node in self.nodes])


def ensure_positive_value(function):
    """Decorator."""
    def inner(*args, **kwargs):
        """Ensures that the value is 0 or positive."""
        value = function(*args, **kwargs)
        if value < 0:
            raise ValueError('Delay value obtained is negative')
        return value
    return inner
