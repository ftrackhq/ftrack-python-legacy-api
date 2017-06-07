# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import ftrack

from .tools import assert_raises
from .test_location import BaseLocationTest


class TestUnmanagedLocation(BaseLocationTest):
    '''Test un-managed location.'''

    def getLocation(self):
        '''Return location instance to test against.'''
        locationName = 'ftrack.test.unmanagedlocation'

        ftrack.ensureLocation(locationName)
        return ftrack.UnmanagedLocation(
            locationName,
            accessor=ftrack.DiskAccessor(prefix=''),
            structure=ftrack.OriginStructure()
        )

    def testAddComponentWithManageDataEnabled(self):
        '''Fail to add component when manageData is True.'''
        component = ftrack.createComponent(path=self.componentPath)
        location = self.getLocation()

        with assert_raises(ftrack.LocationError):
            location.addComponent(component, manageData=True)

    def testRemoveComponentWithManageDataEnabled(self):
        '''Fail to remove component when manageData is True.'''
        component = ftrack.createComponent(path=self.componentPath)
        location = self.getLocation()

        location.addComponent(component)

        with assert_raises(ftrack.LocationError):
            location.removeComponent(component.getId(), manageData=True)

        location.removeComponent(component.getId())

    def testAddComponentMissingTargetAccessor(self):
        '''Add component where target location has no accessor.

        .. note::

            Not relevant for un-managed locations since we do not manage
            any data. Test will always pass.

        '''
        pass

    def testAddComponentDoesntOverwriteFiles(self):
        '''Fail to add component to location if data would be overwritten.

        .. note::

            Not relevant for un-managed locations since we do not manage
            any data. Test will always pass.

        '''
        pass
