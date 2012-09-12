from celery.task import task


@task
def dispatch_event(event_name, event_data):
    # Avoiding a circular import, since we need this task to be called
    # from the "loglib.log()" function.
    from . import process
    process(event_name, event_data)
