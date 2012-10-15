# Eventlib tutorial

## Intro

Long story short, eventlib is an asynchronous event tracking app for
Django. This library was built upon the following values:

 * It must be deadly simple to log an event;
 * It must be possible to track different events in different ways;
 * Each different "event handler" must be completely separate and fail
   gracefully;
 * The event system must be asynchronous, so let's use centry;
 * The library must be extensible;
 * 100% of test coverage is enough.

## Why you need eventlib

Let's imagine that you have a website that sells shoes and you want to
track the access per user in the product page. Initially, your view will
look like this:

```python
@login_required
def product_page(request, pid):
    product = get_object_or_404(pk=pid)
    return render_to_response(context={'product': product})
```

Maybe, the simplest solution for logging the access on the above view
would be just create a model and then add a new row to this model every
time the view processes a request.

But, life is not that fair. Let's make things a little bit more
interesting here. Let's suppose that you also need to increase a counter
in a redis key. So, you'll need to both, create a new row in the db and
make save some stuff in redis.

After a cup of coffee, you get back to your desk, open the bug tracker
and notice that someone just assigned a ticket for you. It says some
thing like: *"Do not increase the redis counter if the product is not
from the source X"*. So, again, I think you'll have to open your
`views.py` file and add an `if` to implement the constraint.

I could waste both my time writing and your time reading millions of
different situations that you need to add a bunch of logic to your view
because of event tracking. And, probably, you would end up with
something like this:

```python
from shoestore.models import ProductViewedEvent

@login_required
def product_page(request, pid):
    product = get_object_or_404(Product, pk=pid)

    # Increasing the redis counter
    if (product.source in ALLOWED_SOURCES) and \
       (product.status == Product.STATUS_PUBLISHED) and \
       (product.is_available_for_shoeprime()) and \
       (user.is_shoeprimecustomer()):
       key = 'shoeprimehit:{}:{}'.format(user.id, product.id)
       conn = redis.StrictRedis()
       conn.incr(key)

    # Logging the user access in the database
    ProductViewedEvent.objects.create(user=user)

    return render_to_response(context={'product': product})
```

You have two lines that actually implement your view and ~10 lines for
logging stuff. Some bad things that the unnecessary coupling between the
view and the logging can cause:

 * Harder to maintain this code;
 * A pain to write tests;
 * If the redis call fail, the mysql call **will** fail, and the user will
   get a nice 500 error page instead of his product.

## Trying again with eventlib

```python
@login_required()
def product_page(request, pid):
    product = get_object_or_404(Product, pk=pid)
    log('shoestore.ProductViewedEvent', {'user: user, 'product: product})
    return render_to_response(context={'product': product})
```

Wait, is that it? Is it everything that you need to do to log your
stuff?  Well, it's pretty much everything you need to do in the
view. Behind the scenes you still have to declare the event itself.

## The event class

To implement the event declared above, you'll need, first, to create a
new file in your django app called `events.py`. Inside this file, you
need to declare your event class, like this:

```python
from eventlib import BaseEvent, handler

class ProductViewedEvent(BaseEvent):

    @handler
    def log_to_mysql(self, data):
        ProductViewedModel.objects.create(user=data['user'])

    @handler
    def log_to_redis(self, data):
        if (product.source in ALLOWED_SOURCES) and \
           (product.status == Product.STATUS_PUBLISHED) and \
           (product.is_available_for_shoeprime()) and \
           (user.is_shoeprimecustomer()):
            key = 'shoeprimehit:{}:{}'.format(user.id, product.id)
            conn = redis.StrictRedis()
            conn.incr(key)
```

Now you're all set. Let's argue about why this approach seems better
than the first one:

 * Decoupled code: If you need to change the logging logic, you don't
   need to touch your views.py file. It's also easier to write tests for
   both view and event.
 * Fault tolerant: If you have an outage in your redis system, your
   customer will still be able to buy shoes, because the event runs
   separately from your business logic (in separate machines if you like
   celery).

## Going further

This tutorial shows only the basic features of eventlib. The next step
is to take a look at the
["Declaring an event and its handlers"](docs/declaring-an-event.md)
page.
