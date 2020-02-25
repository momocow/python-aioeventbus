from typing import Awaitable, Callable, Type

from .event import Event

EventClass = Type[Event]
Handler = Callable[[Event], Awaitable[None]]
