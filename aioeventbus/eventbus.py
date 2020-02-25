import asyncio
from functools import partial
from weakref import WeakKeyDictionary

from .event import Event
from .exceptions import HandlerError


class Listener(WeakKeyDictionary):
    """For better grouping of handlers
    """

    def __init__(self):
        super().__init__()

    def on(self, event, handler=None):
        if not issubclass(event, Event):
            raise TypeError("\"event\" should be a subclass of Event.")

        if handler is None:
            return partial(self.on, event)

        if not asyncio.iscoroutinefunction(handler):
            raise ValueError("\"handler\" should be a coroutine function.")

        if event not in self:
            self[event] = set()
        self[event].add(handler)
        return handler

    def off(self, event=None, handler=None):
        if not issubclass(event, Event):
            raise TypeError("\"event\" should be a subclass of Event.")

        try:
            if handler is not None:
                if event is not None:
                    self[event].remove(handler)
                else:
                    found = False
                    for event in self.keys():
                        if handler in self[event]:
                            self[event].remove(handler)
                            found = True
                            break

                    if not found:
                        raise KeyError(handler)

            else:
                if event is not None:
                    del self[event]
                else:
                    self.clear()
        except KeyError as exc:
            raise KeyError((event, handler)) from exc


class EventBus:
    def __init(self):
        self.__listeners = []

    def register(self, listener):
        self.__listeners.append(listener)

    def unregister(self, listener):
        self.__listeners.remove(listener)

    def _get_events(self, event_obj):
        return event_obj.__class__.__mro__

    def _get_handlers(self, event):
        return (h
                for l in self.__listeners
                for h in l.get(event, []))

    async def _wrap_error(self, handler, event_obj, *,
                          return_exceptions=False):
        try:
            await handler(event_obj)
        except Exception as exc:
            if return_exceptions:
                try:
                    raise HandlerError(handler) from exc
                except HandlerError as exc:
                    return exc
            else:
                raise HandlerError(handler) from exc

    async def emit_series(self, event_obj):
        if not isinstance(event_obj, Event):
            raise TypeError("\"event_obj\" should be an instance of Event.")

        for e in self._get_events(event_obj):
            for h in self._get_handlers(e):
                await self._wrap_error(h, event_obj)
                if event_obj.canceled:
                    return

    async def emit_parallel(self, event_obj, *, return_exceptions=False):
        if not isinstance(event_obj, Event):
            raise TypeError("\"event_obj\" should be an instance of Event.")

        returns = await asyncio.gather(*(self._wrap_error(h, event_obj)
                                      for e in self._get_events(event_obj)
                                      for h in self._get_handlers(e)),
                                    return_exceptions=return_exceptions)
        if return_exceptions:
            return (r for r in returns if isinstance(r, HandlerError))
        
        return ()
