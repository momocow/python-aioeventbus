from abc import ABC
from typing import Awaitable, Callable, Type, Union


class EventBase(ABC):
    pass

EventClass = Type[EventBase]
Handler = Callable[[EventBase], Union[None, Awaitable[None]]]
