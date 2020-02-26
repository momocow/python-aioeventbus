import asyncio
from functools import partial
from inspect import isclass
from typing import Awaitable, Callable, Dict, Optional, Set, Type, TypeVar
from weakref import WeakKeyDictionary

from .event import Event
from .typing import EventClass, Handler


class Listener(WeakKeyDictionary, Dict[EventClass, Set[Handler]]):
    """For better grouping of handlers
    """

    def __init__(self):
        super().__init__()

    def on(self,
           event_cls: EventClass,
           handler: Optional[Handler] = None
           ) -> Optional[Handler]:
        if not issubclass(event_cls, Event):
            raise TypeError("\"event_cls\" should be a subclass of Event.")

        if handler is None:
            return partial(self.on, event_cls)

        if not asyncio.iscoroutinefunction(handler):
            raise ValueError("\"handler\" should be a coroutine function.")

        if event_cls not in self:
            self[event_cls] = []
        self[event_cls].append(handler)
        return handler

    def off(self,
            event_cls: Optional[EventClass] = None, *,
            handler: Optional[Handler] = None
            ):
        if event_cls is not None and not issubclass(event_cls, Event):
            raise TypeError("\"event_cls\" should be a subclass of Event.")

        try:
            if handler is not None:
                if event_cls is not None:
                    self[event_cls].remove(handler)
                else:
                    found = False
                    for event_cls in self.keys():
                        if handler in self[event_cls]:
                            self[event_cls].remove(handler)
                            found = True
                            break

                    if not found:
                        raise KeyError(handler)

            else:
                if event_cls is not None:
                    del self[event_cls]
                else:
                    self.clear()
        except KeyError as exc:
            raise LookupError((event_cls, handler)) from exc

    def __bool__(self):
        return any(bool(self[event_cls]) for event_cls in self)

    def __repr__(self):
        events = ", ".join(f"{event_cls.__name__}: {len(self[event_cls])}"
                           for event_cls in self)
        return "{cls} {{{events}}}".format(cls=self.__class__.__name__,
                                           events=events)

    def __contains__(self, o):
        if asyncio.iscoroutinefunction(o):
            return any(o in self[event_cls] for event_cls in self)
        if isclass(o) and issubclass(o, Event):
            return super().__contains__(o)
        return False
