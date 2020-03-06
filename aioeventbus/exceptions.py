from .typing import EventBase, Handler


class HandlerError(Exception):
    def __init__(self, handler: Handler, event: EventBase):
        handler_name = handler.__name__ if hasattr(handler, "__name__") \
            else repr(handler)
        super().__init__(f"Handler {handler_name} failed "
                         f"during handling {repr(event)}")
        self.handler = handler
        self.event = event


class InvalidState(Exception):
    pass
