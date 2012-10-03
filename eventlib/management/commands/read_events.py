from django.conf import settings
from django.core.management.base import BaseCommand

from eventlib.core import process_external
from eventlib.ejson import loads
from eventlib.exceptions import EventNotFoundError
from eventlib.util import redis_connection


class Command(BaseCommand):

    def handle(self, *args, **options):
        conn = redis_connection.get_connection()
        pubsub = conn.pubsub()
        pubsub.subscribe("eventlib")
        while True:
            message = next(pubsub.listen())
            if message['type'] != 'message':
                continue
            data = loads(message["data"])
            if 'name' in data:
                event_name = data.pop('name')
                process_external(event_name, data)
