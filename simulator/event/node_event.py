"""Events related with a node object are coded here."""
from .base_event import _BaseEvent


class _NodeEvent(_BaseEvent):
    """Base class for the events of a Node."""

    def __init__(self, event_time, node):
        super().__init__(event_time)
        self.node = node


class DataSent(_NodeEvent):
    """Event generated when a node start trying to send data to the medium."""
    def __init__(self, event_time, node, data):
        super().__init__(event_time, node)
        self.data = data


class DataReceived(_NodeEvent):
    """Event generated when a node receive data from the medium."""
    def __init__(self, event_time, node, data):
        super().__init__(event_time, node)
        self.data = data


class NodeWakesUp(_NodeEvent):
    """Event generated when a node wakes up."""

    def __init__(self, event_time, node):
        super().__init__(event_time, node)

    def execute(self):
        print(f'{self.time}Node {node.name} is awake')
