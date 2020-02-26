# python-aioeventbus
Simple, in-process, event-driven programming for Python based on asyncio.

## Quick Start
```py
from aioeventbus import event, Event, Listener
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
def on_my_event():
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

### Error Handing

#### LookupError
This error is raised when calling `bus.off(event_cls, handler)` with any of `event_cls` or `handler` is not `None` and the lookup for the specified event or handler failed.

#### InvalidState
This error is raised when access the global context variable `event` outside the handler scope.

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
