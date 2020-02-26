from contextlib import suppress
from contextvars import ContextVar
from typing import Any, Dict, Generic, TypeVar

from .exceptions import InvalidState
from .typing import EventBase

Context = TypeVar("Context")

class ContextProxy(Generic[Context]):
    def __init__(self, var: ContextVar[Context]):
        self.__v = var
    
    @property
    def __ctx__(self) -> ContextVar[Context]:
        return self.__v

    @property
    def __ctx(self) -> Context:
        try:
            return self.__v.get()
        except LookupError:
            raise InvalidState(f"context unbound")

    @property
    def __dict__(self) -> Dict[str, Any]:  # type: ignore
        try:
            return self.__ctx.__dict__
        except InvalidState:
            raise AttributeError("__dict__")

    def __repr__(self) -> str:
        try:
            return repr(self.__ctx)
        except InvalidState:
            return f"<{self.__class__.__name__} unbound>"

    def __bool__(self) -> bool:
        with suppress(InvalidState):
            return bool(self.__ctx)
        return False

    def __dir__(self) -> Any:
        try:
            return dir(self.__ctx)
        except RuntimeError:
            return []

    def __getattr__(self, name: str):
        return getattr(self.__ctx, name)
    
    def __getitem__(self, name: Any) -> Any:
        return self.__ctx[name]
    
    def __setitem__(self, name: Any, value: Any):
        self.__ctx[name] = value
    
    def __delitem__(self, name: Any):
        del self.__ctx[name]
