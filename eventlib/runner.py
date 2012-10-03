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
