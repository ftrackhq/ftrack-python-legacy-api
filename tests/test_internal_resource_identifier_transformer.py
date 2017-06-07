# :coding: utf-8
# :copyright: Copyright (c) 2014 FTrack

import os
import platform as _platform
from uuid import uuid4 as uuid
import ftrack

from ftrack import InternalResourceIdentifierTransformer
from .test_resource_identifier_transformer import (
    TestResourceIdentifierTransformer
)

from .tools import assert_equal, assert_raises


class TestInternalResourceIdentifierTransformer(
    TestResourceIdentifierTransformer
):
    '''Test InternalResourceIdentifierTransformer.'''

    def setUp(self):
        '''Perform per test setup.'''
        self.assetPathPrefix = ftrack.getAssetPathPrefix()

        workflow = ftrack.getProjectSchemes()[0]

        name = 'location-testproject-{0}'.format(uuid().hex)
        self.project = ftrack.createProject(name, name, workflow)
        self.project.set('root', 'my_project_root_test')

        shot = self.project.createShot('010')
        asset = shot.createAsset('tmp', 'geo')
        version = asset.createVersion()

        self.component = version.createComponent('preview')

        version.publish()

        # Figure out disk prefix for current OS and project.
        platform = _platform.system()
        self.diskPrefix = None

        for disk in ftrack.getDisks():
            if disk.get('diskid') == self.project.get('diskid'):

                if platform in ('Darwin', 'Linux'):
                    self.diskPrefix = disk.get('unix')
                elif platform in ('Windows'):
                    self.diskPrefix = disk.get('windows')

        if self.diskPrefix is None:
            raise NotImplementedError(
                'Platform {0} not supported'.format(platform)
            )

    def _testPath(self, resourceIdentifier, matchThis, diskPrefix=''):
        '''Test *resourceIdentifier* is equal to *matchThis* after transform.'''
        transformer = InternalResourceIdentifierTransformer()

        context = {
            'component': self.component
        }

        matchThis = os.path.join(
            diskPrefix,
            matchThis
        )

        assert_equal(
            transformer.decode(resourceIdentifier, context=context),
            matchThis
        )

    def testEncode(self):
        '''Encode resource identifier.'''
        resourceIdentifier = 'test.identifier'
        transformer = InternalResourceIdentifierTransformer()

        assert_equal(transformer.encode(resourceIdentifier), resourceIdentifier)

    def testEncodeWithContext(self):
        '''Encode resource identifier using context.'''
        resourceIdentifier = 'test.identifier'
        transformer = InternalResourceIdentifierTransformer()

        assert_equal(
            transformer.encode(resourceIdentifier, context={}),
            resourceIdentifier
        )

    def testDecodeWithoutContext(self):
        '''Fail to decode resource identifier without context.'''
        resourceIdentifier = 'test.identifier'
        transformer = InternalResourceIdentifierTransformer()

        with assert_raises(ValueError):
            assert_equal(
                transformer.decode(resourceIdentifier),
                resourceIdentifier
            )

    def testDecodeWithoutComponent(self):
        '''Fail to decode resource identifier without component in context.'''
        resourceIdentifier = 'test.identifier'
        transformer = InternalResourceIdentifierTransformer()

        with assert_raises(KeyError):
            assert_equal(
                transformer.decode(resourceIdentifier, context={}),
                resourceIdentifier
            )

    def testDecodeWithContext(self):
        '''Decode resource identifier with context.'''
        transformer = InternalResourceIdentifierTransformer()

        resourceIdentifier = 'some/random/path'

        context = {
            'component': self.component
        }

        # Decode should happen without any exceptions.
        result = transformer.decode(resourceIdentifier, context=context)

        assert_equal(
            result,
            os.path.join(
                self.diskPrefix,
                'my_project_root_test/ftrack/assets/some/random/path'
            )
        )

    def testDecodeWithRelativePath(self):
        '''Decode resource identifier with relative disk.'''
        resourceIdentifier = 'path/to/file.png'
        self._testPath(
            resourceIdentifier,
            os.path.join(
                self.diskPrefix,
                self.project.get('root'),
                self.assetPathPrefix,
                resourceIdentifier
            )
        )

    def testDecodeAbsolutePathUnixMatched(self):
        '''Decode absolute linux path with matched disk.'''
        self._testPath(
            '/tmp/path/to/file.png',
            'path/to/file.png',
            self.diskPrefix
        )

    def testDecodeAbsolutePathWindowsMatched(self):
        '''Decode absolute windows path with matched disk.'''
        self._testPath(
            'c:\\ftrack\\test\\path\\to\\file.png',
            'path\\to\\file.png',
            self.diskPrefix
        )

    def testDecodeAbsolutePathUnixNotMatched(self):
        '''Decode absolute linux path with non-matched disk.'''
        self._testPath(
            '/un-matched-disk/path/to/file.png',
            '/un-matched-disk/path/to/file.png'
        )

    def testDecodeAbsolutePathWindowsNotMatched(self):
        '''Decode absolute windows path with non-matched disk.'''
        self._testPath(
            'c:\\path\\to\\file.png',
            'c:\\path\\to\\file.png'
        )

    def testDecodeAbsolutePathMountedWindowsNotMatched(self):
        '''Decode absolute mounted windows path and non-matched disk.'''
        self._testPath(
            '\\\\path\\to\\file.png',
            '\\\\path\\to\\file.png'
        )

    def testDecodeAbsolutePathFileSequenceUnMatchedUnixDisk(self):
        '''Decode absolute unix file sequence path with un-matched disk.'''
        self._testPath(
            '/mypath/file_bad.%03d.jpg [1-5]',
            '/mypath/file_bad.%03d.jpg [1-5]'
        )

    def testDecodeAbsolutePathFileSequenceWithMatchedUnixDisk(self):
        '''Decode absolute unix file sequence path with matched disk.'''
        self._testPath(
            '/tmp/file_bad.%03d.jpg [1-5]',
            'file_bad.%03d.jpg [1-5]',
            self.diskPrefix
        )

    def testDecodeAbsolutePathFileSequenceUnMatchedWindowsDisk(self):
        '''Decode absolute windows file sequence path with un-matched disk.'''
        self._testPath(
            'c:\\file_bad.%03d.jpg [1-5]',
            'c:\\file_bad.%03d.jpg [1-5]'
        )

    def testDecodeAbsolutePathFileSequenceWithMatchedWindowsDisk(self):
        '''Decode absolute windows file sequence path with matched disk.'''
        self._testPath(
            'c:\\ftrack\\test\\file_bad.%03d.jpg [1-5]',
            'file_bad.%03d.jpg [1-5]',
            self.diskPrefix
        )
