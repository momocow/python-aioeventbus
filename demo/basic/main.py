import asyncio
import time

from aioeventbus import EventBus, Listener
from events import LifecycleEvent, ShutdownEvent, StartupEvent

listener_1 = Listener()
listener_2 = Listener()

events = []


@listener_1.on(LifecycleEvent)
async def on_lifecycle(event):
    print("Lifecycle event:", event.time, f"({time.time() - event.time})")
    events.append(event)


@listener_2.on(StartupEvent)
async def on_startup(event):
    await asyncio.sleep(2)
    print(event, f"({time.time() - event.time})")


@listener_2.on(ShutdownEvent)
async def on_shutdown(event):
    print(event, f"({time.time() - event.time})")
    await asyncio.sleep(2)


async def main():
    bus = EventBus()
    bus.register(listener_1)
    bus.register(listener_2)

    startup_event = StartupEvent()
    await bus.emit_parallel(startup_event)

    shutdown_event = ShutdownEvent()
    await bus.emit_series(shutdown_event)

    assert events == [startup_event, shutdown_event]

if __name__ == "__main__":
    asyncio.run(main())
