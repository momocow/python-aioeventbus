import asyncio
import time

from aioeventbus import EventBus, Listener, Event
from events import LifecycleEvent, ShutdownEvent, StartupEvent

listener_1 = Listener()
listener_2 = Listener()
listener_3 = Listener()

class LonelyEvent(Event):
    pass


@listener_1.on(LifecycleEvent)
async def on_lifecycle(event):
    print("on_lifecycle")

@listener_1.on(Event)
def on_all_events(event):
    print("all events come here")

@listener_2.on(StartupEvent)
async def on_startup(event):
    print("on_startup")
    event["hello"] = "world"


@listener_2.on(ShutdownEvent)
async def on_shutdown(event):
    print("on_shutdown")

    event["bye"] = "world"

@listener_3.on(LifecycleEvent)
async def on_lifecycle_bus2(event):
    print("on_lifecycle_bus2")

async def main():
    bus = EventBus()
    bus2 = EventBus()

    bus.register(listener_1)
    bus.register(listener_2)
    bus2.register(listener_3)

    bus.pipe(bus2)

    startup_event = StartupEvent()
    # just like `await asyncio.gather()`
    print("emit startup")
    await bus.emit_series(startup_event)

    shutdown_event = ShutdownEvent()
    # execute one by one
    print("emit shutdown")
    await bus.emit_parallel(shutdown_event,
                            return_exceptions=False)

    assert startup_event["hello"] == "world"
    assert shutdown_event["bye"] == "world"

if __name__ == "__main__":
    asyncio.run(main())
