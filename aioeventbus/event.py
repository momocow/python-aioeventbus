from abc import ABC
    

class Event(ABC):
    def __init__(self):
        self.__canceled = False

    @property
    def name(self):
        return self.__class__.__name__
    
    @property
    def canceled(self):
        return self.__canceled
    
    def cancel(self):
        self.__canceled = True

    def __repr__(self):
        return "<Event {0}>".format(self.__class__.name)
    