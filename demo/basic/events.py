import time

from aioeventbus import Event


class LifecycleEvent(Event):
    def __init__(self):
        self.time = time.time()


class StartupEvent(LifecycleEvent):
    pass


class ShutdownEvent(LifecycleEvent):
    pass
