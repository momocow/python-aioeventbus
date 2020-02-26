import asyncio
import time

from aioeventbus import EventBus, Listener, event, Event
from events import LifecycleEvent, ShutdownEvent, StartupEvent

listener_1 = Listener()
listener_2 = Listener()
listener_3 = Listener()

class LonelyEvent(Event):
    pass


@listener_1.on(LifecycleEvent)
async def on_lifecycle():
    print("on_lifecycle")


@listener_2.on(StartupEvent)
async def on_startup():
    print("on_startup")
    event["hello"] = "world"


@listener_2.on(ShutdownEvent)
async def on_shutdown():
    print("on_shutdown")

    event["bye"] = "world"

@listener_3.on(LifecycleEvent)
async def on_lifecycle_bus2():
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
    await bus.emit_parallel(startup_event,
                            return_exceptions=False)

    shutdown_event = ShutdownEvent()
    # execute one by one
    await bus.emit_series(shutdown_event)

    assert startup_event["hello"] == "world"
    assert shutdown_event["bye"] == "world"

if __name__ == "__main__":
    asyncio.run(main())
