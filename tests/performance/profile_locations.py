# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

'''Profile performance of locations API.'''

try:
    import cProfile as profile
except ImportError:
    import profile

import pstats
import timeit
import tempfile
import os
from uuid import uuid4 as uuid
import argparse
import sys

import ftrack


def printHeader(value, marker='-'):
    '''Print a header with *value* using *marker*.'''
    print marker * 80
    print value
    print marker * 80


class Base(object):
    '''Base class.

    Subclass from this for convenient setup of profile and time test cases.

    '''

    def printHeader(self, value):
        '''Print a header with *value*.'''
        printHeader(value, marker='-')

    def setup(self):
        '''Prepare.

        Override this method to perform any test setup that should not be
        included in the timings.

        Return values that should be passed to :py:meth:`~Base.run` as
        positional arguments.

        '''
        # Clear caches.
        ftrack.cache.memoiser.cache.clear()
        ftrack.clearGetCache()
        ftrack.xmlServer.resetStatistics()

        return tuple()

    def teardown(self, *args):
        '''Cleanup after test using *args* returned from setup.'''

    def run(self, *options):
        '''Code to test.

        Override in subclasses.

        '''
        raise NotImplementedError()

    def profile(self):
        '''Profile execution of code in run method and output results.'''
        self.printHeader('Profiling...')
        profiler = profile.Profile()
        options = self.setup()
        if not isinstance(options, tuple):
            options = (options, )

        try:
            profiler.enable()
            self.run(*options)
            profiler.disable()
        finally:
            self.teardown(*options)

        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative', 'time', 'calls')
        stats.print_stats('FTrackCore|clique')

    def time(self, count=10):
        '''Repeat test a number of times and output timing information.'''
        self.printHeader('Timing...')
        timer = timeit.Timer(
            'try: test.run(*options); finally: test.teardown(*options);',
            'from __main__ import {0}; test = {0}(); options = test.setup();'
            .format(self.__class__.__name__)
        )
        times = timer.repeat(count, 1)
        print 'Total: {0}'.format(sum(times))
        print (
            'Average: {0} (Fastest: {1}, Slowest: {2})'
            .format(
                sum(times) / count,
                min(times),
                max(times)
            )
        )

        print 'Values (Sorted): {0}'.format(sorted(times))
        print 'Values (Running Order): {0}'.format(times)

    def requests(self):
        '''Count server requests, cache hits etc.'''
        self.printHeader('Recording requests...')
        options = self.setup()
        if not isinstance(options, tuple):
            options = (options, )

        ftrack.xmlServer.resetStatistics()

        try:
            self.run(*options)
            statistics = ftrack.xmlServer.getStatistics()

        finally:
            self.teardown(*options)

        for key, value in sorted(statistics.items()):
            print '{0}: {1}'.format(key, value)


class AddComponent(Base):
    '''Profile Location.addComponent method.'''

    def setup(self):
        '''Prepare test.

        Create and return:

            * A temporary location with a disk accessor and id structure.
            * A component in the origin location only.

        '''
        super(AddComponent, self).setup()

        locationName = 'location-{0}'.format(uuid().hex)
        location = ftrack.ensureLocation(locationName)
        prefix = os.path.join(tempfile.gettempdir(), 'ftrack', locationName)
        location.setAccessor(ftrack.DiskAccessor(prefix=prefix))
        location.setStructure(ftrack.IdStructure())
        location.setPriority(1)

        component = ftrack.createComponent(
            'test', path='test.jpg', location=None
        )

        return location, component

    def teardown(self, version, location):
        '''Cleanup.'''
        ftrack.LOCATION_PLUGINS.discard(location)
        location.delete()

    def run(self, location, component):
        '''Run addComponent method on *location* with *component*.

        .. note::

            Data management is **not** included.

        '''
        location.addComponent(component, manageData=False)


class CreateComponent(Base):
    '''Profile createComponent function.'''

    def setup(self):
        '''Prepare test.

        Create and return:

            * A temporary location with a disk accessor and id structure that
              has been added to the location plugins list with highest priority.
            * A path to a sequence of 10 frames.

        '''
        super(CreateComponent, self).setup()

        locationName = 'location-{0}'.format(uuid().hex)
        location = ftrack.ensureLocation(locationName)
        prefix = os.path.join(tempfile.gettempdir(), 'ftrack', locationName)
        location.setAccessor(ftrack.DiskAccessor(prefix=prefix))
        location.setStructure(ftrack.IdStructure())
        location.setPriority(1)

        ftrack.LOCATION_PLUGINS.add(location)

        path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), '..', 'data', 'sequence_10',
                'file.%03d.jpg [1-10]'
            )
        )

        return path, location

    def teardown(self, version, location):
        '''Cleanup.'''
        ftrack.LOCATION_PLUGINS.discard(location)
        location.delete()

    def run(self, path, location):
        '''Run createComponent for *path*.

        .. note::

            Also includes management of data.

        '''
        ftrack.createComponent(path=path)


class GetComponents(Base):
    '''Profile getComponents function.'''

    def setup(self):
        '''Prepare test.

        Create and return:

            * Two temporary locations with a disk accessor and id structure.
              Both are added to the location plugins registry with highest
              priority.
            * A version with 10 components added to the temporary location with
              the second highest priority.

        '''
        super(GetComponents, self).setup()

        locations = []
        for index in range(2):
            locationName = 'location-{0}'.format(uuid().hex)
            location = ftrack.ensureLocation(locationName)
            prefix = os.path.join(tempfile.gettempdir(), 'ftrack', locationName)
            location.setAccessor(ftrack.DiskAccessor(prefix=prefix))
            location.setStructure(ftrack.IdStructure())
            location.setPriority(index)

            ftrack.LOCATION_PLUGINS.add(location)
            locations.append(location)

        path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), '..', 'data', 'attachment.txt'
            )
        )

        shot = ftrack.getShot(['bunny', 'seq1', '0102'])
        task = shot.getTasks()[0]
        asset = shot.createAsset(name='testAsset', assetType='geo')
        version = asset.createVersion(
            comment='A test comment.',
            taskid=task.getId()
        )

        for index in range(10):
            version.createComponent(
                name='component_{0:03d}'.format(index + 1),
                path=path,
                location=locations[-1] # Second highest priority location.
            )

        version.publish()

        return version, locations

    def teardown(self, version, locations):
        '''Cleanup.'''
        for location in locations:
            ftrack.LOCATION_PLUGINS.discard(location)
            location.delete()

    def run(self, version, locations):
        '''Run getComponents for *version*.'''
        components = version.getComponents()


class Choices(object):
    '''Handle default list with choices.

    See http://bugs.python.org/issue9625.

    '''

    def __init__(self, choices, *args, **kw):
        '''Initialise type.'''
        super(Choices, self).__init__(*args, **kw)
        self._choices = choices

    def __call__(self, value):
        '''Handle *value*.'''
        if value not in self._choices:
            raise argparse.ArgumentTypeError(
                'invalid choice: {0!r} (choose from {1})'
                .format(
                    value, ', '.join([
                        repr(choice) for choice in self._choices
                    ])
                )
            )

        return value


def main(arguments=None):
    '''Execute performance tests.'''
    if arguments is None:
        arguments = []

    tests = {
        'addComponent': AddComponent(),
        'createComponent': CreateComponent(),
        'getComponents': GetComponents()
    }

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'tests', nargs='*', default=tests.keys(), type=Choices(tests.keys())
    )

    suites = {
        'profile': 'profile',
        'time': 'time',
        'requests': 'requests'
    }
    for suite in suites.keys():
        parser.add_argument(
            '--{0}'.format(suite),
            action='store_true', help='Run {0} suite.'.format(suite)
        )

    namespace = parser.parse_args(arguments)

    for test in namespace.tests:
        printHeader(test, marker='=')

        ranSuite = False

        for suite, methodName in sorted(suites.items()):
            if getattr(namespace, suite.replace('-', '_'), False):
                getattr(tests[test], methodName)()
                ranSuite = True

        if not ranSuite:
            print 'No test suites selected to run.'


if __name__ == '__main__':
    main(sys.argv[1:])
    raise SystemExit()
