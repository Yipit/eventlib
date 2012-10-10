from eventlib.core import process_external, import_event_modules
from eventlib.ejson import loads
from eventlib.util import redis_connection


def listen_for_events():
    import_event_modules()
    conn = redis_connection.get_connection()
    pubsub = conn.pubsub()
    pubsub.subscribe("eventlib")
    for message in pubsub.listen():
        if message['type'] != 'message':
            continue
        data = loads(message["data"])
        if 'name' in data:
            event_name = data.pop('name')
            process_external(event_name, data)
