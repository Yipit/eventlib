from mock import patch

import eventlib
from eventlib import core


def test_handler_registry():
    core.cleanup_handlers()

    @eventlib.handler('stuff.Klass')
    def do_nothing(data):
        return len(data)

    core.HANDLER_REGISTRY.should.have.length_of(1)
    core.HANDLER_REGISTRY['stuff.Klass'].should.be.equals([do_nothing])


def test_handler_with_methods():
    core.cleanup_handlers()

    class MyEvent(eventlib.BaseEvent):

        @eventlib.handler
        def handle_stuff(self):
            pass

    core.HANDLER_REGISTRY.should.have.length_of(1)
    core.HANDLER_REGISTRY[MyEvent].should.be.equals([MyEvent.handle_stuff])


def test_handler_registry_cleanup():
    core.cleanup_handlers()
    core.HANDLER_REGISTRY.should.have.length_of(0)

    @eventlib.handler('stuff.Klass')
    def do_nothing(data):
        return -1

    @eventlib.handler('stuff.Blah')
    def do_another_nothing(data):
        return 0

    core.HANDLER_REGISTRY.should.have.length_of(2)
    core.HANDLER_REGISTRY['stuff.Klass'].should.be.equals([do_nothing])
    core.HANDLER_REGISTRY['stuff.Blah'].should.be.equals([do_another_nothing])

    core.cleanup_handlers('stuff.Klass')
    dict(core.HANDLER_REGISTRY).should.be.equals(
        {'stuff.Blah': [do_another_nothing]})

    core.cleanup_handlers()
    core.HANDLER_REGISTRY.should.have.length_of(0)


@patch('eventlib.core.find_event')
def test_find_handlers(find_event):
    core.cleanup_handlers()

    @eventlib.handler('app.Event')
    def stuff(data):
        return 0
    core.find_handlers('app.Event').should.be.equals([stuff])

    @eventlib.handler('app.Event')
    def other_stuff(data):
        return 1
    core.find_handlers('app.Event').should.be.equals([stuff, other_stuff])

    @eventlib.handler('app.Event2')
    def more_stuff(data):
        return 2
    core.find_handlers('app.Event').should.be.equals([stuff, other_stuff])
    core.find_handlers('app.Event2').should.be.equals([more_stuff])

    core.find_handlers('dont.Exist').should.be.equal([])


@patch('eventlib.core.find_event')
def test_find_handlers_with_mixed_objects_and_strings(find_event):
    core.cleanup_handlers()

    class MyEvent(eventlib.BaseEvent):
        @eventlib.handler
        def handle_stuff(self):
            pass

    find_event.return_value = MyEvent

    @eventlib.handler('stuff.MyEvent')
    def do_nothing(data):
        return len(data)

    core.find_handlers('stuff.MyEvent').should.be.equals([
        MyEvent.handle_stuff, do_nothing
    ])
