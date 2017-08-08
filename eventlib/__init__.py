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

"""implementation of the RFC00001-event-log-spec proposal"""

# Registering the serializers for eventlib
import ejson.serializers        # pyflakes:ignore

# Imports to register and expose things in the "eventlib" namespace.
from .api import log, handler, external_handler, BaseEvent  # pyflakes: ignore


__version__ = '0.1.6'

__all__ = (
    'BaseEvent', 'handler', 'external_handler', 'log',
)
