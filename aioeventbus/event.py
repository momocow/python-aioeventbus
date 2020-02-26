from collections.abc import MutableMapping
from reprlib import recursive_repr
from typing import Any, Iterator

from .typing import EventBase


class Event(MutableMapping, EventBase):
    def __init__(self):
        self.__g = {}

    def __getitem__(self, name: Any) -> Any:
        return self.__g[name]

    def __setitem__(self, name: Any, value: Any):
        self.__g[name] = value

    def __delitem__(self, name: Any):
        del self.__g[name]

    def __iter__(self) -> Iterator[Any]:
        return iter(self.__g)

    def __len__(self) -> int:
        return len(self.__g)
    
    def __str__(self) -> str:
        return repr(self)

    @recursive_repr()
    def __repr__(self) -> str:
        return f"<Event: {self.__class__.__name__}>"
