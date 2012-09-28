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

from setuptools import setup, find_packages
from pkg_resources import require


if __name__ == '__main__':
    setup(
        name="eventlib",
        version=require('eventlib')[0].version,
        description=(
            u'Library to make it easy to track events in python/django apps'),
        author=u'Lincoln de Sousa',
        author_email=u'lincoln@yipit.com',
        url='https://github.com/Yipit/eventlib',
        packages=find_packages(),
    )
