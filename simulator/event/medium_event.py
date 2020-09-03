"""Events related with a medium object are coded here."""
from .base_event import _BaseEvent


class PacketLeftNode(_BaseEvent):
    """Event generated when a packet is sent to the medium."""

    def __init__(self, event_time, node, data):
        super().__init__(event_time)
        self.node = node
        self.data = data


class PacketReachNode(_BaseEvent):
    """Event generated when a packet arrive to a node from medium."""

    def __init__(self, event_time, node, data):
        super().__init__(event_time)
        self.node = node
        self.data = data
