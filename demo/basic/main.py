import time

from aioeventbus import EventBus, Listener

from events import LifecycleEvent, ShutdownEvent, StartupEvent

listener_1 = Listener()
listener_2 = Listener()

@listener_1.on(LifecycleEvent)
async def on_lifecycle(event):
    print("Lifecycle event:", event.time)

@listener_2.on(StartupEvent)
async def on_startup(event):
    print(event)

@listener_2.on(ShutdownEvent)
async def on_shutdown(event):
    print(event)

async def main():
    bus = EventBus()
    bus.register(listener_1)
    bus.register(listener_2)
    await bus.emit_parallel(StartupEvent())
    await bus.emit_parallel(ShutdownEvent())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
