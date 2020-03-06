from __future__ import annotations

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
        self.__children: List[EventBus] = []

    def register(self, *listeners: Listener):
        self.__listeners.extend(listeners)

    def unregister(self, *listeners: Listener):
        for l in listeners:
            self.__listeners.remove(l)

    def clear(self):
        return self.__listeners.clear()

    def get_propagation_order(self, event: EventBase) -> Tuple[EventClass]:
        return event.__class__.__mro__[:-1]  # exclude object class

    def get_handlers(self, event_cls: EventClass) -> Tuple[Handler]:
        return (h
                for l in self.__listeners
                for h in l.get(event_cls, []))

    @contextmanager
    def __event_context(self, event: EventBase):
        token = None
        prev_event = event_v.get(None)
        if prev_event is not event:
            token = event_v.set(event)
        yield
        if token is not None:
            event_v.reset(token)

    async def __call_handler(self,
                             handler: Handler,
                             event: EventBase, *,
                             return_exceptions: bool = False
                             ) -> Optional[HandlerError]:
        try:
            # create handler context
            ret = handler(event)
            if asyncio.iscoroutine(ret):
                await asyncio.create_task(ret)
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
            for e in self.get_propagation_order(event):
                for h in self.get_handlers(e):
                    try:
                        await self.__call_handler(h, event,
                                                  return_exceptions=False)
                    except (StopIteration, StopAsyncIteration):
                        return

            for c in self.__children:
                await c.emit_series(event)

    async def emit_parallel(self, event: EventBase, *,
                            return_exceptions: bool = False
                            ) -> Tuple[HandlerError]:
        if not isinstance(event, Event):
            raise TypeError("\"event\" should be an instance of Event.")

        with self.__event_context(event):
            coros = list(
                self.__call_handler(h, event,
                                    return_exceptions=return_exceptions)
                for e in self.get_propagation_order(event)
                for h in self.get_handlers(e)
            )
            coros_len = len(coros)
            child_coros = (
                c.emit_parallel(event,
                                return_exceptions=return_exceptions)
                for c in self.__children
            )
            returns = await asyncio.gather(*coros, *child_coros,
                                           return_exceptions=return_exceptions)

        return tuple(r for r in returns[:coros_len]
                     if isinstance(r, HandlerError)) + \
            tuple(r for rs in returns[coros_len:] for r in rs)

    def pipe(self, bus: EventBus):
        self.__children.append(bus)

    def unpipe(self, bus: EventBus):
        self.__children.remove(bus)

    def attach(self, bus: EventBus):
        bus.pipe(self)

    def detach(self, bus: EventBus):
        bus.unpipe(self)

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
