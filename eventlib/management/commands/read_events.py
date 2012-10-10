from django.core.management.base import BaseCommand

from eventlib.listener import listen_for_events


class Command(BaseCommand):

    def handle(self, *args, **options):
        listen_for_events()
