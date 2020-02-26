from .typing import EventBase, Handler


class HandlerError(Exception):
    def __init__(self, handler: Handler, event: EventBase):
        super().__init__(f"Handler {handler.__name__} failed "
                         f"during handling {repr(event)}")
        self.handler = handler
        self.event = event


class InvalidState(Exception):
    pass
