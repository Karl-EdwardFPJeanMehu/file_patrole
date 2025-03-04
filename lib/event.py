import asyncio

# Observer registry
registry = dict()

def subscribe(event_type: str, fn):
    event_type = event_type.lower()
    if event_type not in registry:
        registry[event_type] = []
    registry[event_type].append(fn)

# Dispatcher to handle async and async observers
async def dispatch_observer(event_type: str, data):
    event_type = event_type.lower()
    event = registry.get(event_type)

    if event is None:
        raise ValueError(f"Observer {event_type} not found!")

    for fn in event:
        if asyncio.iscoroutinefunction(fn):
            await fn(data)
        else:
            await asyncio.to_thread(fn, data)

def post_event(event_type: str, data):
    asyncio.run(dispatch_observer(event_type, data))
