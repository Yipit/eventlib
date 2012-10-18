# Eventlib tutorial (p3)

This is the third article about event lib, the second one was about how
to ["Declaring an events"](p2-declaring-an-event.md).

Here we explain how the handlers are processed asynchronously and what
you need to do to serialize data to send through celery.

## Events are not immediately processed

Usually, logging events is pretty useful for getting metrics about
resource access, to understand how the user interact with a product, to
find a performance bottleneck, etc.

But, none of these uses are tied to the business logic, so, this kind of
code should be separate from the views and models of your application.

Another very common requirement for logging is to execute more than one
action for a specific event. And usually, these actions don't depend on
each other.

This way, we came up with the idea of executing handlers separately.
This is the basic flow of a logging operation:

```
 ----------------------------
|eventlib.log('event', data) |
 ----------------------------
    v
   -----------------
  | serialize(data) |
   -----------------
    v
   ---------------------
  | celery_task.delay() |
   ---------------------
    v
   ------------------
  | deserialize(data) |
   ------------------
    v
   ------------------------
  | find_handlers('event') |
   ------------------------
    v
   -------------------------------
  | process_each_handler(handler) |
   -------------------------------
```

The data must be serialized in order to be sent through the celery
backend.
