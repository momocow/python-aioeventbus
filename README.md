# python-aioeventbus
Simple, in-process, event-driven programming for Python based on asyncio.

## Quick Start
```py
import time

from aioeventbus import Event, EventBus, Listener


class MyEvent1(Event):
    pass

class MyEvent2(MyEvent1):
    pass

listener = Listener()

@listener.on(MyEvent1)
async def my_handler1(event):
    # because MyEvent2 is extended from MyEvent1
    # MyEvent2 event will also trigger MyEvent1 handlers
    assert isinstance(event, MyEvent2)

@listener.on(MyEvent2)
async def my_handler2(event):
    assert isinstance(event, MyEvent2)

async def main():
    bus = EventBus()
    bus.register(listener)
    await bus.emit_series(MyEvent2())

if __name__ == "__main__":
    asyncio.run(main())
```

