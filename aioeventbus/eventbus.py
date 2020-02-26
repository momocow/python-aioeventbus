import asyncio
from contextlib import contextmanager
from typing import List, Optional, Tuple, Type

from .event import Event
from .exceptions import HandlerError
from .globals import event_v
from .listener import Listener
from .typing import EventBase, EventClass, Handler


class EventBus:
    def __init__(self):
        self.__listeners: List[Listener] = []

    def register(self, *listeners: Listener):
        self.__listeners.extend(listeners)

    def unregister(self, *listeners: Listener):
        for l in listeners:
            self.__listeners.remove(l)

    def clear(self):
        return self.__listeners.clear()

    def _get_events(self, event: EventBase) -> Tuple[EventClass]:
        return event.__class__.__mro__[:-1]  # exclude object class

    def _get_handlers(self, event_cls: EventClass) -> Tuple[Handler]:
        return (h
                for l in self.__listeners
                for h in l.get(event_cls, []))

    @contextmanager
    def __event_context(self, event: EventBase):
        token = event_v.set(event)
        yield
        event_v.reset(token)

    async def __call_handler(self,
                             handler: Handler,
                             event: EventBase, *,
                             return_exceptions: bool = False
                             ) -> Optional[HandlerError]:
        try:
            # create handler context
            await asyncio.create_task(handler())
        except Exception as exc:
            if return_exceptions:
                try:
                    raise HandlerError(handler, event) from exc
                except HandlerError as exc:
                    return exc
            else:
                raise HandlerError(handler, event) from exc

    async def emit_series(self, event: EventBase):
        if not isinstance(event, Event):
            raise TypeError("\"event\" should be an instance of Event.")

        with self.__event_context(event):
            for e in self._get_events(event):
                for h in self._get_handlers(e):
                    try:
                        await self.__call_handler(h, event,
                                                  return_exceptions=False)
                    except (StopIteration, StopAsyncIteration):
                        return

    async def emit_parallel(self, event: EventBase, *,
                            return_exceptions: bool = False
                            ) -> Tuple[HandlerError]:
        if not isinstance(event, Event):
            raise TypeError("\"event\" should be an instance of Event.")

        with self.__event_context(event):
            coros = (
                self.__call_handler(h, event,
                                    return_exceptions=return_exceptions)
                for e in self._get_events(event)
                for h in self._get_handlers(e)
            )
            returns = await asyncio.gather(*coros)

        return (r for r in returns if isinstance(r, HandlerError))

    @property
    def events(self):
        return set(e for l in self.__listeners for e in l)

    def __len__(self):
        return len(self.events)

    def __bool__(self):
        return any(bool(l) for l in self.__listeners)

    def __contains__(self, o):
        if isinstance(o, Listener):
            return o in self.__listeners
        return any(o in l for l in self.__listeners)
