from contextvars import ContextVar

from .proxy import ContextProxy
from .typing import EventBase

event_v: ContextVar[EventBase] = ContextVar("event")
event: ContextProxy[EventBase] = ContextProxy(event_v)
