# python-aioeventbus
Simple, in-process, event-driven programming for Python3.7+ based on asyncio.

## Quick Start
```py
from aioeventbus import Event, Listener
```

### Define an Event
```py
class MyEvent(Event):
    def __init__(self, data):
        self.data = data
```

### Listen on the Event
```py
listener = Listener()
expected_data = iter(range(5))

# use decorator
@listener.on(MyEvent)
def on_my_event(event):
    assert event.data == next(expected_data)

# or function call
listener.on(MyEvent, on_my_event)
```

### Emit the Event
```py
bus = EventBus()
bus.register(listener)
for i in range(5):
    # emit handlers in series
    # use this if order is an issue for you
    await bus.emit_series(MyEvent(i))

    # or emit them concurrently
    # return a list of HandlerError if return_exceptions is True
    await bus.emit_parallel(MyEvent(i),
                            return_exceptions=False)
```

Nothing happens if an Event without any handlers is emitted.

```py
class NoBodyCareThisEvent(Event):
    pass

await bus.emit_series(NoBodyCareThisEvent())
```

### Clean up
```py
listener.off()
# or
listener.off(MyEvent)
# or
listener.off(handler=on_my_event)
# or
listener.off(MyEvent, on_my_event)

bus.clear()
# or
bus.unregister(listener)
```

### Pipe buses
```py
child_bus = EventBus()

bus.pipe(child_bus)
# or
child_bus.attach(bus)
```

After piping, events emitted on `bus` will also be emitted onto `child_bus`.

### Unpipe buses
```py
bus.unpipe(child_bus)
# or
child_bus.detach(bus)
```

### Error Handing

#### LookupError
This error is raised when calling `bus.off(event_cls, handler)` with any of `event_cls` or `handler` is not `None` and the lookup for the specified event or handler failed.


#### HandlerError
```py
@listener.on(MyEvent)
def on_my_bug_event():
    raise Exception("test")

try:
    await bus.emit_series(MyEvent())
except HandlerError as exc:
    print(exc.event)
    print(exc.handler)

    import traceback
    traceback.print_exc()
```

```
<Event: MyEvent>
<function on_my_bug_event at ...>
Traceback (most recent call last):
  ...
Exception: test

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  ...
aioeventbus.exceptions.HandlerError: Handler on_my_bug_event failed during handling <Event: MyEvent>
```
