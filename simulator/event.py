"""Module with code related to the events of the simulator."""


class Event:
    """Base class for the events of the simulator."""

    def __init__(self, event_id, event_time):
        self.id = event_id
        self.time = event_time
        pass
