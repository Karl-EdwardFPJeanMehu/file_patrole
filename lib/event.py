subscribers = dict()

def subscribe(event_type: str, fn):
    event_type = event_type.lower()
    if not event_type in subscribers:
        subscribers[event_type] = []
    subscribers[event_type].append(fn)

def post_event(event_type: str, data):
    event_type = event_type.lower()
    if not event_type in subscribers:
        return
    for fn in subscribers[event_type]:
        fn(data)

