# eventlib - Copyright (c) 2012  Yipit, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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


def test_external_handler_with_methods():
    core.cleanup_handlers()

    @eventlib.external_handler('stuff.Klass')
    def handle_stuff(self):
        pass

    core.EXTERNAL_HANDLER_REGISTRY.should.have.length_of(1)
    core.EXTERNAL_HANDLER_REGISTRY['stuff.Klass'].should.be.equals([handle_stuff])


def test_handler_registry_cleanup():
    core.cleanup_handlers()
    core.HANDLER_REGISTRY.should.have.length_of(0)

    @eventlib.handler('stuff.Klass')
    def do_nothing(data):
        return -1

    @eventlib.handler('stuff.Blah')
    def do_another_nothing(data):
        return 0

    @eventlib.external_handler('stuff.Foobar')
    def do_more_nothing(data):
        return 0

    @eventlib.external_handler('stuff.Foobaz')
    def do_a_lot_more_nothing(data):
        return 0

    core.HANDLER_REGISTRY.should.have.length_of(2)
    core.HANDLER_REGISTRY['stuff.Klass'].should.be.equals([do_nothing])
    core.HANDLER_REGISTRY['stuff.Blah'].should.be.equals([do_another_nothing])

    core.EXTERNAL_HANDLER_REGISTRY.should.have.length_of(2)
    core.EXTERNAL_HANDLER_REGISTRY['stuff.Foobar'].should.be.equals([do_more_nothing])
    core.EXTERNAL_HANDLER_REGISTRY['stuff.Foobaz'].should.be.equals([do_a_lot_more_nothing])

    core.cleanup_handlers('stuff.Klass')
    dict(core.HANDLER_REGISTRY).should.be.equals({
        'stuff.Blah': [do_another_nothing],
    })

    core.cleanup_handlers('stuff.Foobaz')
    dict(core.EXTERNAL_HANDLER_REGISTRY).should.be.equals({
        'stuff.Foobar': [do_more_nothing],
    })

    core.cleanup_handlers()
    core.HANDLER_REGISTRY.should.have.length_of(0)
    core.EXTERNAL_HANDLER_REGISTRY.should.have.length_of(0)


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

    @eventlib.external_handler('app2.Event')
    def still_more_stuff(data):
        return 3
    core.find_external_handlers('app2.Event').should.be.equals([still_more_stuff])

    core.find_handlers('dont.Exist').should.be.equal([])
    core.find_external_handlers('dont.Exist').should.be.equal([])


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
