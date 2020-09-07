"""Module with code related to the events of the simulator."""
from uuid import uuid4


class _BaseEvent:
    """Base class for the events of the simulator."""

    def __init__(self, event_time):
        self.id = uuid4()
        self.time = event_time
        pass
