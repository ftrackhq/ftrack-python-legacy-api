# :coding: utf-8
# :copyright: Copyright (c) 2017 ftrack

import os
import re

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
SOURCE_PATH = os.path.join(ROOT_PATH, 'source')
README_PATH = os.path.join(ROOT_PATH, 'README.rst')

# Read version from source.
with open(os.path.join(
    SOURCE_PATH, 'FTrackCore', 'api', 'version_data.py')
) as _version_file:
    VERSION = re.match(
        r'.*ftrackVersion = \'(.*?)\'', _version_file.read(), re.DOTALL
    ).group(1)


# Configuration.
setup(
    name='ftrack-python-legacy-api',
    version=VERSION,
    description='The ftrack legacy python api.',
    long_description=open(README_PATH).read(),
    keywords='ftrack, api',
    url='https://bitbucket.org/ftrack/ftrack-python-legacy-api',
    author='ftrack',
    author_email='support@ftrack.com',
    license='Apache License (2.0)',

    packages=find_packages(SOURCE_PATH),
    package_dir={
        '': 'source'
    },
    setup_requires=[
        'sphinx >= 1.2.2, < 2',
        'sphinx_rtd_theme >= 0.1.6, < 2',
        'lowdown >= 0.1.0, < 2'
    ],
    install_requires=[
        'pyparsing >= 2.0.1, < 3',
        'clique >= 1.2.0, < 2',
        'requests >= 2.2.0, < 3',
        'websocket-client >= 0.40.0, < 1',
        'six >= 1.5.2'
    ],
    tests_require=[
        'nose >= 1.3',
        'boto >= 2.4'
    ],

    test_suite='nose.collector',
    zip_safe=False,
)
