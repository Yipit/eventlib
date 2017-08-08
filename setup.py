# eventlib - Smart/Async event logging library
#
# Copyright (c) 2012-2013  Lincoln Clarete <lincoln@comum.org>
# Copyright (c) 2012-2013  Yipit, Inc <coders@yipit.com>
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

import os
import re
from setuptools import setup, find_packages


def parse_requirements():
    """Rudimentary parser for the `requirements.txt` file

    We just want to separate regular packages from links to pass them to the
    `install_requires` and `dependency_links` params of the `setup()`
    function properly.
    """
    try:
        requirements = \
            map(str.strip, local_file('requirements.txt').split('\n'))
    except IOError:
        raise RuntimeError("Couldn't find the `requirements.txt' file :(")

    links = []
    pkgs = []
    for req in requirements:
        if not req:
            continue
        if 'http:' in req or 'https:' in req:
            links.append(req)
            name, version = re.findall("\#egg=([^\-]+)-(.+$)", req)[0]
            pkgs.append('{0}=={1}'.format(name, version))
        else:
            pkgs.append(req)

    return pkgs, links


local_file = lambda f: \
    open(os.path.join(os.path.dirname(__file__), f)).read()


install_requires, dependency_links = parse_requirements()


if __name__ == '__main__':
    setup(
        name="eventlib-pyqs",
        version='0.1.6',
        description=(
            u'Library to make it easy to track events in python/django apps'),
        long_description=local_file('README.md'),
        author=u'Lincoln de Sousa',
        author_email=u'lincoln@yipit.com',
        url='https://github.com/Yipit/eventlib',
        packages=filter(lambda n: not n.startswith('tests'), find_packages()),
        install_requires=install_requires,
        dependency_links=dependency_links,
        entry_points={
            'console_scripts': [
                'eventlib = eventlib.runner:main',
            ],
        },
    )
