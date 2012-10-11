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

from logan.runner import run_app

import base64
import os

KEY_LENGTH = 40

CONFIG_TEMPLATE = """
import os.path

CONF_ROOT = os.path.dirname(__file__)

CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

INSTALLED_APPS = (
    'eventlib',
)

REDIS_CONNECTIONS = {
    'default': {
        'HOST': 'localhost',
        'PORT': 6379,
    },
}
"""


def generate_settings():
    """
    This command is run when ``default_path`` doesn't exist, or ``init`` is
    run and returns a string representing the default data to put into their
    settings file.
    """
    output = CONFIG_TEMPLATE % dict(
        default_key=base64.b64encode(os.urandom(KEY_LENGTH)),
    )

    return output


def main():
    run_app(
        project='eventlib',
        default_config_path='~/.eventlib/',
        settings_initializer=generate_settings,
        settings_envvar='EVENTLIB_CONF',
    )

if __name__ == '__main__':
    main()
