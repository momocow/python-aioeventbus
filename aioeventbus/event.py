from abc import ABC
    

class Event(ABC):
    @property
    def name(self) -> str:
        return self.__class__.__name__

    def __repr__(self) -> str:
        return "<Event {0}>".format(self.__class__.name)
    