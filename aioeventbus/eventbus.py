import asyncio
from typing import List, Optional, Tuple, Type

from .event import Event
from .exceptions import HandlerError
from .listener import Listener
from .types import EventClass, Handler


class EventBus:
    def __init(self):
        self.__listeners: List[Listener] = []

    def register(self, *listeners: Listener):
        self.__listeners.extend(listeners)

    def unregister(self, *listeners: Listener):
        for l in listeners:
            self.__listeners.remove(l)

    def _get_events(self, event: Event) -> Tuple[EventClass]:
        return event.__class__.__mro__[:-1]  # exclude object class

    def _get_handlers(self, event_cls: EventClass) -> Tuple[Handler]:
        return (h
                for l in self.__listeners
                for h in l.get(event_cls, []))

    async def __call_handler(self,
                             handler: Handler,
                             event: Event, *,
                             return_exceptions: bool = False
                             ) -> Optional[HandlerError]:
        try:
            await handler(event)
        except Exception as exc:
            if return_exceptions:
                try:
                    raise HandlerError(handler, event) from exc
                except HandlerError as exc:
                    return exc
            else:
                raise HandlerError(handler, event) from exc

    async def emit_series(self, event: Event):
        if not isinstance(event, Event):
            raise TypeError("\"event\" should be an instance of Event.")

        for e in self._get_events(event):
            for h in self._get_handlers(e):
                try:
                    await self.__call_handler(h, event)
                except (StopIteration, StopAsyncIteration):
                    return

    async def emit_parallel(self, event: Event, *,
                            return_exceptions: bool = False
                            ) -> Tuple[HandlerError]:
        if not isinstance(event, Event):
            raise TypeError("\"event\" should be an instance of Event.")

        returns = await asyncio.gather(*(self.__call_handler(h, event)
                                         for e in self._get_events(event)
                                         for h in self._get_handlers(e)),
                                       return_exceptions=return_exceptions)
        if return_exceptions:
            return (r for r in returns if isinstance(r, HandlerError))

        return ()
