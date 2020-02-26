from abc import ABC
from typing import Awaitable, Callable, Type


class EventBase(ABC):
    pass

EventClass = Type[EventBase]
Handler = Callable[[EventBase], Awaitable[None]]
