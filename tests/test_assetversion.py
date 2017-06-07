# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os
from uuid import uuid4 as uuid

import ftrack

from .tools import ok_, assert_equal, assert_raises, assert_raises_regexp


class TestAssetVersion(object):
    '''Test AssetVersion.'''

    def __init__(self):
        '''Initialise test.'''
        self.dataPath = os.path.join(os.path.dirname(__file__), 'data')
        self.componentPath = os.path.join(
            self.dataPath, 'sequence', 'file.001.jpg'
        )

    def setUp(self):
        '''Perform per test setup.'''

    def tearDown(self):
        '''Perform per test teardown.'''

    def _generateVersion(self):
        '''Return new version.'''
        showName = 'show-{0}'.format(uuid().hex)
        show = ftrack.createShow(
            showName, showName,
            ftrack.ProjectScheme('VFX Scheme')
        )

        sequenceName = 'sequence-{0}'.format(uuid().hex)
        sequence = show.createSequence(sequenceName)

        asset = sequence.createAsset(name='version_test', assetType='geo')
        version = asset.createVersion()

        return version

    def testGetComponents(self):
        '''Retrieve components for asset version.'''
        version = self._generateVersion()
        location = ftrack.Location('location_a')

        componentA = version.createComponent(
            name='a',
            path=self.componentPath,
            location=location
        )

        componentB = version.createComponent(
            name='b',
            path=self.componentPath,
            location=None
        )

        retrievedVersion = ftrack.AssetVersion(version.getId())
        components = retrievedVersion.getComponents()

        componentIds = []
        for component in components:
            componentIds.append(component.getId())

            if component.getName() == 'a':
                assert_equal(component.getLocation().getId(), location.getId())
            elif component.getName() == 'b':
                assert_equal(component.getLocation(), None)

        assert_equal(len(componentIds), 2)
        for component in (componentA, componentB):
            ok_(
                component.getId() in componentIds,
                'Component {0} missing from retrieved components.'
                .format(component.getName())
            )

    def testGetComponentsSpecifyingLocation(self):
        '''Retrieve components for asset version specifying location.'''
        version = self._generateVersion()
        location = ftrack.Location('location_a')

        componentA = version.createComponent(
            name='a',
            path=self.componentPath,
            location=location
        )

        componentB = version.createComponent(
            name='b',
            path=self.componentPath,
            location=location
        )

        retrievedVersion = ftrack.AssetVersion(version.getId())

        # Retrieve components specifying correct location.
        components = retrievedVersion.getComponents(location=location)
        componentIds = [component.getId() for component in components]

        assert_equal(len(componentIds), 2)
        for component in components:
            assert_equal(component.getLocation().getId(), location.getId())

            ok_(
                component.getId() in componentIds,
                'Component {0} missing from retrieved components.'
                .format(component.getName())
            )

        # Retrieve components specifying no location.
        components = retrievedVersion.getComponents(location=None)
        componentIds = [component.getId() for component in components]

        assert_equal(len(componentIds), 2)
        for component in components:
            assert_equal(component.getLocation(), None)

            ok_(
                component.getId() in componentIds,
                'Component {0} missing from retrieved components.'
                .format(component.getName())
            )
