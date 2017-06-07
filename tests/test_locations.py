# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack

import os
from uuid import uuid4 as uuid

import ftrack

from .tools import ok_, assert_equal, assert_raises, assert_raises_regexp


class TestLocations(object):
    '''Test locations API methods.'''

    def __init__(self):
        '''Initialise test.'''
        self.dataPath = os.path.join(os.path.dirname(__file__), 'data')
        self.componentPath = os.path.join(
            self.dataPath, 'sequence', 'file.001.jpg'
        )
        self.componentSequencePath = os.path.join(
            self.dataPath, 'sequence', 'file.%03d.jpg'
        )

    def setUp(self):
        '''Perform per test setup.'''

    def tearDown(self):
        '''Perform per test teardown.'''

    def _generateRandomVersion(self):
        showName = 'show-{0}'.format(uuid().hex)
        show = ftrack.createShow(showName, showName,
                                 ftrack.ProjectScheme('VFX Scheme'))

        sequenceName = 'sequence-{0}'.format(uuid().hex)
        sequence = show.createSequence(sequenceName)

        asset = sequence.createAsset(name='component_test', assetType='geo')
        version = asset.createVersion()

        return version

    def createRandomLocation(self):
        '''Return a new location with a unique name.'''
        name = 'location-{0}'.format(uuid().hex)
        location = ftrack.createLocation(name)
        return location

    def testGetLocations(self):
        '''Retrieve locations.'''
        locations = ftrack.getLocations()
        ok_(len(locations) > 0, 'No locations retrieved.')
        ok_(isinstance(locations, ftrack.FTList), 'Instance is not FTList.')

    def testGetLocationsCache(self):
        '''Retrieve all locations when using cache.'''
        locations = ftrack.getLocations()
        locationCount = len(locations)
        ok_(locationCount > 0, 'No locations retrieved.')

        # Create a new location through the API.
        location = self.createRandomLocation()

        # Ensure correct result retrieved (cache was cleared).
        locations = ftrack.getLocations()
        ok_(len(locations) > locationCount, 'New location not included.')

        match = None
        for candidate in locations:
            if candidate.getId() == location.getId():
                match = candidate
                break

        ok_(match is not None, 'New location not included.')

    def testGetLocationsExcludingHidden(self):
        '''Retrieve locations excluding those that are hidden.'''
        locations = ftrack.getLocations(includeHidden=False)
        for location in locations:
            if location.getName() == 'ftrack.origin':
                raise AssertionError(
                    'Hidden location incorrectly included in results.'
                )

    def testGetLocationsIncludingHidden(self):
        '''Retrieve locations including those that are hidden.'''
        locations = ftrack.getLocations(includeHidden=True)
        found = False
        for location in locations:
            if location.getName() == 'ftrack.origin':
                found = True
                break

        if not found:
            raise AssertionError(
                'Hidden location incorrectly excluded from results.'
            )

    def testGetLocationsExcludingInaccessible(self):
        '''Retrieve all accessible locations.'''
        locations = ftrack.getLocations(excludeInaccessible=True)
        for location in locations:
            if location.getName() == 'location_without_accessor':
                raise AssertionError(
                    'Inaccessible location incorrectly included in results.'
                )

    def testGetLocationsIncludingInaccessible(self):
        '''Retrieve locations regardless of accessibility.'''
        locations = ftrack.getLocations(excludeInaccessible=False)
        found = False
        for location in locations:
            if location.getName() == 'location_without_accessor':
                found = True
                break

        if not found:
            raise AssertionError(
                'Inaccessible location incorrectly excluded from results.'
            )

    def testCreateLocation(self):
        '''Create a new location.'''
        name = 'location-{0}'.format(uuid().hex)
        location = ftrack.createLocation(name)
        assert_equal(location.get('name'), name)

    def testCreateExistingLocation(self):
        '''Fail creating location with same name as existing one.'''
        location = self.createRandomLocation()

        with assert_raises_regexp(ftrack.FTrackError, 'Duplicate name'):
            ftrack.createLocation(location.getName())

    def testEnsureLocation(self):
        '''Ensure a location that doesn't exist.'''
        name = 'location-{0}'.format(uuid().hex)
        with assert_raises(ftrack.FTrackError):
            ftrack.Location(name)

        ftrack.ensureLocation(name)
        location = ftrack.Location(name)
        assert_equal(location.getName(), name)

    def testEnsureExistingLocation(self):
        '''Ensure a location that already exists.'''
        location = self.createRandomLocation()
        ensuredLocation = ftrack.ensureLocation(location.getName())
        assert_equal(location.getId(), ensuredLocation.getId())

    def testDeleteLocation(self):
        '''Delete an existing empty location.'''
        location = self.createRandomLocation()

        # Assert that retrieving location fails after deletion.
        location.delete()

        with assert_raises_regexp(ftrack.FTrackError, ''):
            ftrack.Location(location.getName())

    def testDeleteLocationWithComponents(self):
        '''Fail to delete a location with components.'''
        location = self.createRandomLocation()
        location.setStructure(ftrack.OriginStructure())

        component = ftrack.createComponent(
            path=self.componentPath
        )
        location.addComponent(component, manageData=False)

        with assert_raises_regexp(ftrack.FTrackError, 'contains components'):
            location.delete()

    def testDeleteEmptiedLocation(self):
        '''Delete a location emptied of components.'''
        location = self.createRandomLocation()
        location.setStructure(ftrack.OriginStructure())

        component = ftrack.createComponent(
            path=self.componentPath
        )
        location.addComponent(component, manageData=False)
        with assert_raises_regexp(ftrack.FTrackError, 'contains components'):
            location.delete()

        location.removeComponent(component.getId(), manageData=False)
        location.delete()

    def testDeleteBuiltinLocation(self):
        '''Fail to delete a built-in location.'''
        location = ftrack.Location('ftrack.origin')
        with assert_raises_regexp(ftrack.FTrackError, 'built-in location'):
            location.delete()

    def testRenameBuiltinLocation(self):
        '''Fail to rename a built-in location.'''
        location = ftrack.Location('ftrack.origin')
        with assert_raises_regexp(ftrack.FTrackError, 'Update Error'):
            location.set('name', 'foo')

    def testGetComponentAvailability(self):
        '''Calculate component availability.'''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )

        # Check initial availability in all locations is 0.0
        availability = {}
        for location in ftrack.getLocations():
            availability[location.getId()] = 0.0

        assert_equal(
            ftrack.getComponentAvailability(component.getId()),
            availability
        )

        # Check availability for location_a is 100.0 after adding component.
        location = ftrack.Location('location_a')
        location.addComponent(component)

        assert_equal(
            ftrack.getComponentAvailability(
                component.getId(), [location.getId()]
            ),
            {
                location.getId(): 100.0
            }
        )

    def testGetComponentAvailabilities(self):
        '''Calculate multiple component availabilities.'''
        componentA = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )

        componentB = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )

        componentIds = [componentA.getId(), componentB.getId()]

        # Check initial availability in all locations is 0.0
        availabilities = []
        for _ in componentIds:
            availability = {}
            for location in ftrack.getLocations():
                availability[location.getId()] = 0.0

            availabilities.append(availability)

        assert_equal(
            ftrack.getComponentAvailabilities(componentIds),
            availabilities
        )

        # Check availability for location_a is 100.0 after adding component.
        location = ftrack.Location('location_a')
        location.addComponent(componentB)
        availabilities[1][location.getId()] = 100.0

        assert_equal(
            ftrack.getComponentAvailabilities(componentIds),
            availabilities
        )

        # Check when passing explicit location ids.
        availabilities = [
            {location.getId(): 0.0},
            {location.getId(): 100.0},
        ]

        assert_equal(
            ftrack.getComponentAvailabilities(componentIds, [location.getId()]),
            availabilities
        )

    def testPickLocation(self):
        '''Pick appropriate location.'''
        location = ftrack.pickLocation()
        assert_equal(location.getName(), 'location_a')

    def testPickLocationForSpecificComponent(self):
        '''Pick appropriate location for retrieving component.'''
        locationA = ftrack.Location('location_a')
        componentA = ftrack.createComponent(
            path=self.componentPath, location=locationA
        )

        assert_equal(
            ftrack.pickLocation(componentId=componentA.getId()).getId(),
            locationA.getId()
        )

        locationB = ftrack.Location('location_b')
        componentB = ftrack.createComponent(
            path=self.componentPath, location=locationB
        )

        assert_equal(
            ftrack.pickLocation(componentId=componentB.getId()).getId(),
            locationB.getId()
        )

        componentC = ftrack.createComponent(
            path=self.componentPath, location=None
        )

        assert_equal(
            ftrack.pickLocation(componentId=componentC.getId()),
            None
        )

    def testPickLocations(self):
        '''Pick appropriate locations for retrieving components.'''
        locationA = ftrack.Location('location_a')
        componentA = ftrack.createComponent(
            path=self.componentPath, location=locationA
        )

        locationB = ftrack.Location('location_b')
        componentB = ftrack.createComponent(
            path=self.componentPath, location=locationB
        )

        componentC = ftrack.createComponent(
            path=self.componentPath, location=None
        )

        picked = ftrack.pickLocations(
            componentIds=[
                componentA.getId(),
                componentB.getId(),
                componentC.getId()
            ]
        )
        for index, location in enumerate(picked):
            if location is not None:
                picked[index] = location.getId()

        expected = [
            locationA.getId(),
            locationB.getId(),
            None
        ]

        assert_equal(picked, expected)
