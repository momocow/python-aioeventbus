from .types import Event, EventClass, Handler


class HandlerError(Exception):
    def __init__(self, handler: Handler, event: Event):
        super().__init__(f"{handler} failed during handling {event}")
        self.handler = handler
        self.event = event
