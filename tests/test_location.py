# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack

import os
import glob
from uuid import uuid4 as uuid

import clique
import ftrack

from .tools import ok_, assert_equal, assert_raises


class AlwaysTheSameStructure(ftrack.Structure):

    def getResourceIdentifier(self, entity):
        '''Always return the same identifier.'''
        return 'hard/coded/identifier'


class BaseLocationTest(object):
    '''Test base location implementation.'''

    def __init__(self):
        '''Initialise test.'''
        self.dataPath = os.path.join(os.path.dirname(__file__), 'data')
        self.componentPath = os.path.join(
            self.dataPath, 'sequence', 'file.001.jpg'
        )

        collections, _ = clique.assemble(
            glob.glob(os.path.join(self.dataPath, 'sequence', '*.jpg'))
        )
        self.sequenceCollection = collections[0]
        self.sequenceComponentDescription = self.sequenceCollection.format()

    def setUp(self):
        '''Perform per test setup.'''

    def tearDown(self):
        '''Perform per test teardown.'''

    def getLocation(self):
        '''Return location instance to test against.'''
        raise NotImplementedError()

    def getRandomizedLocationName(self):
        '''Return a new unique location name.'''
        return 'location-{0}'.format(uuid().hex)

    def createRandomLocation(self):
        '''Return a new location with a unique name.'''
        name = self.getRandomizedLocationName()
        location = ftrack.createLocation(name)
        return location

    def testKeys(self):
        '''Return keys.'''
        location = self.createRandomLocation()

        assert_equal(
            location.keys(),
            ['description', 'entityId', 'entityType', 'htest', 'id',  'label',
            'name']
        )

    def testSetName(self):
        '''Test setting new location name.'''
        location = self.createRandomLocation()
        newName = 'location-{0}'.format(uuid().hex)
        location.set('name', newName)

        assert_equal(location.get('name'), newName)

        locationViaNewName = ftrack.Location(newName)
        assert_equal(location.get('id'), locationViaNewName.get('id'))

    def testSetGetAccessor(self):
        '''Test setting and retrieving accessor.'''
        location = self.createRandomLocation()

        mock_accessor = object()
        assert_equal(location.getAccessor(), None)
        location.setAccessor(mock_accessor)
        assert_equal(location.getAccessor(), mock_accessor)

    def testAddComponent(self):
        '''Add component to location.'''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        componentId = component.getId()
        location = self.getLocation()

        assert_equal(location.getComponentAvailability(componentId), 0.0)

        component = location.addComponent(component)
        assert_equal(location.getComponentAvailability(componentId), 100.0)

    def testAddContainerComponent(self):
        '''Add container component to location.'''
        component = ftrack.createComponent(
            path=self.sequenceComponentDescription,
            location=None
        )
        componentId = component.getId()
        location = self.getLocation()

        assert_equal(location.getComponentAvailability(componentId), 0.0)
        for member in component.getMembers():
            assert_equal(
                location.getComponentAvailability(member.getId()), 0.0
            )

        component = location.addComponent(component)

        assert_equal(location.getComponentAvailability(componentId), 100.0)
        for member in component.getMembers():
            assert_equal(
                location.getComponentAvailability(member.getId()), 100.0
            )

    def testAddExistingComponent(self):
        '''Fail to add component to location twice.'''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        componentId = component.getId()
        location = self.getLocation()

        component = location.addComponent(component)
        assert_equal(location.getComponentAvailability(componentId), 100.0)

        with assert_raises(ftrack.ComponentInLocationError):
            location.addComponent(component)

    def testAddComponentMissingTargetAccessor(self):
        '''Fail to add component where target location has no accessor.'''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        targetLocation = self.getLocation()
        currentAccessor = targetLocation.getAccessor()

        try:
            targetLocation.setAccessor(None)
            with assert_raises(ftrack.LocationError):
                targetLocation.addComponent(component)
        finally:
            targetLocation.setAccessor(currentAccessor)

    def testAddComponentMissingTargetStructure(self):
        '''Fail to add component where target location has no structure.'''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        targetLocation = self.getLocation()
        currentStructure = targetLocation.getStructure()

        try:
            targetLocation.setStructure(None)
            with assert_raises(ftrack.LocationError):
                targetLocation.addComponent(component)
        finally:
            targetLocation.setStructure(currentStructure)

    def testAddComponentWithoutManagingData(self):
        '''Add component to location without managing its data.'''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        componentId = component.getId()
        location = self.getLocation()

        # Force specific settings for predictable testing.
        location.setStructure(ftrack.IdStructure())

        # Ensure it is not available.
        assert_equal(location.getComponentAvailability(componentId), 0.0)

        # Add component without managing data.
        component = location.addComponent(component, manageData=False)

        # Ensure it is available in the location.
        assert_equal(location.getComponentAvailability(componentId), 100.0)

        # Check that no data exists in target location.
        ok_(
            not location.getAccessor().exists(
                component.getResourceIdentifier()
            ),
            'Data existed after adding to location despite manageData=False.'
        )

    def testAddComponentDoesntOverwriteFiles(self):
        '''Fail to add component to location if data would be overwritten.'''
        componentA = ftrack.createComponent(
            path=self.componentPath, location=None
        )
        componentB = ftrack.createComponent(
            path=self.componentPath, location=None
        )
        location = self.getLocation()

        originalStructure = location.getStructure()
        structure = AlwaysTheSameStructure()
        try:
            location.setStructure(structure)
            location.addComponent(componentA)

            with assert_raises(ftrack.LocationError):
                location.addComponent(componentB)

        finally:
            location.getAccessor().remove(
                structure.getResourceIdentifier(None)
            )
            location.setStructure(originalStructure)

    def testAdoptComponent(self):
        '''Test adopting component from location.'''
        location = self.getLocation()
        component = ftrack.createComponent(
            path=self.componentPath,
            location=location,
        )

        retrievedComponent = ftrack.Component(
            id=component.getId(), location=None
        )
        assert_equal(retrievedComponent.getLocation(), None)
        assert_equal(retrievedComponent.getResourceIdentifier(), None)

        location.adoptComponent(retrievedComponent)

        assert_equal(retrievedComponent.getLocation(), location)

        resourceIdentifier = location.getStructure().getResourceIdentifier(
            retrievedComponent
        )
        assert_equal(
            retrievedComponent.getResourceIdentifier(), resourceIdentifier
        )
        ok_(retrievedComponent.getFilesystemPath() is not None)

    def testAdoptComponents(self):
        '''Adopt multiple components from location.'''
        location = self.getLocation()
        componentA = ftrack.createComponent(
            path=self.componentPath,
            location=location,
        )

        componentB = ftrack.createComponent(
            path=self.componentPath,
            location=location,
        )

        retrievedComponentA = ftrack.Component(
            id=componentA.getId(), location=None
        )

        retrievedComponentB = ftrack.Component(
            id=componentB.getId(), location=None
        )

        for retrievedComponent in (retrievedComponentA, retrievedComponentB):
            assert_equal(retrievedComponent.getLocation(), None)
            assert_equal(retrievedComponent.getResourceIdentifier(), None)

        location.adoptComponents([retrievedComponentA, retrievedComponentB])

        for retrievedComponent in (retrievedComponentA, retrievedComponentB):
            assert_equal(retrievedComponent.getLocation(), location)

            resourceIdentifier = location.getStructure().getResourceIdentifier(
                retrievedComponent
            )
            assert_equal(
                retrievedComponent.getResourceIdentifier(), resourceIdentifier
            )
            ok_(retrievedComponent.getFilesystemPath() is not None)

    def testGetComponent(self):
        '''Test retrieving component from location.'''
        location = self.getLocation()
        component = ftrack.createComponent(
            path=self.componentPath,
            location=location,
        )

        retrievedComponent = location.getComponent(component.getId())
        assert_equal(retrievedComponent.getId(), component.getId())
        assert_equal(retrievedComponent.getLocation().getId(),
                     location.getId())

        resourceIdentifier = location.getStructure().getResourceIdentifier(
            component
        )
        assert_equal(
            retrievedComponent.getResourceIdentifier(), resourceIdentifier
        )
        ok_(retrievedComponent.getFilesystemPath() is not None)

    def testGetComponents(self):
        '''Retrieve multiple components from location.'''
        location = self.getLocation()
        componentA = ftrack.createComponent(
            path=self.componentPath,
            location=location,
        )
        componentB = ftrack.createComponent(
            path=self.componentPath,
            location=location,
        )

        retrievedComponents = location.getComponents([
            componentA.getId(), componentB.getId()
        ])

        for retrievedComponent in retrievedComponents:
            assert_equal(
                retrievedComponent.getLocation().getId(), location.getId()
            )

            resourceIdentifier = location.getStructure().getResourceIdentifier(
                retrievedComponent
            )
            assert_equal(
                retrievedComponent.getResourceIdentifier(), resourceIdentifier
            )
            ok_(retrievedComponent.getFilesystemPath() is not None)

    def testGetAllComponents(self):
        '''Retrieve all components from location.'''
        location = self.createRandomLocation()
        location.setStructure(ftrack.IdStructure())

        components = []
        numberOfComponents = 10
        for index in xrange(numberOfComponents):
            components.append(
                ftrack.createComponent(
                    path=self.componentPath,
                    location=location,
                    manageData=False
                )
            )

        retrievedComponents = location.getComponents()
        count = 0

        for retrievedComponent in retrievedComponents:
            count += 1

            assert_equal(
                retrievedComponent.getLocation().getId(), location.getId()
            )

            resourceIdentifier = location.getStructure().getResourceIdentifier(
                retrievedComponent
            )
            assert_equal(
                retrievedComponent.getResourceIdentifier(), resourceIdentifier
            )

        assert_equal(count, numberOfComponents)

    def testGetComponentFromLocationWithNoAccessor(self):
        '''Retrieve component from location with no accessor.'''
        location = self.getLocation()
        component = ftrack.createComponent(
            path=self.componentPath,
            location=location
        )

        currentAccessor = location.getAccessor()
        try:
            location.setAccessor(None)
            retrievedComponent = location.getComponent(component.getId())
            ok_(retrievedComponent.getFilesystemPath() is None)
        finally:
            location.setAccessor(currentAccessor)

    def testGetComponentWithAccessorLackingFilesystemPathSupport(self):
        '''Retrieve component from location with lack of filesystem path.'''
        location = self.getLocation()
        component = ftrack.createComponent(
            path=self.componentPath,
            location=location
        )

        accessor = location.getAccessor()
        originalGetFilesystemPath = accessor.getFilesystemPath

        def getFilesystemPath(self, path):
            raise ftrack.AccessorUnsupportedOperationError(
                'getFilesystemPath', path=path
            )

        try:
            accessor.getFilesystemPath = getFilesystemPath.__get__(
                accessor, accessor.__class__
            )
            retrievedComponent = location.getComponent(component.getId())
            ok_(retrievedComponent.getFilesystemPath() is None)
        finally:
            del accessor.getFilesystemPath

    def testGetComponentNotInLocation(self):
        '''Test retrieving component that is not in location.'''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        location = self.getLocation()

        with assert_raises(ftrack.ComponentNotInLocationError):
            location.getComponent(component.getId())

    def testGetComponentsNotInLocation(self):
        '''Test retrieving multiple components that are not in location.'''
        componentA = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        componentB = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        location = self.getLocation()

        with assert_raises(ftrack.ComponentNotInLocationError):
            location.getComponents([
                componentA.getId(),
                componentB.getId()
            ])

    def testRemoveComponent(self):
        '''Remove component from location.'''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None,
        )

        location = self.getLocation()
        component = location.addComponent(component)

        assert_equal(
            location.getComponentAvailability(component.getId()),
            100.0
        )

        location.removeComponent(component.getId())

        assert_equal(
            location.getComponentAvailability(component.getId()),
            0.0
        )

    def testRemoveContainerComponent(self):
        '''Remove container component from location.'''
        component = ftrack.createComponent(
            path=self.sequenceComponentDescription,
            location=None
        )

        location = self.getLocation()
        component = location.addComponent(component)

        assert_equal(
            location.getComponentAvailability(component.getId()),
            100.0
        )
        for member in component.getMembers():
            assert_equal(
                location.getComponentAvailability(member.getId()), 100.0
            )

        location.removeComponent(component.getId())
        assert_equal(
            location.getComponentAvailability(component.getId()),
            0.0
        )
        for member in component.getMembers(location=None):
            assert_equal(
                location.getComponentAvailability(member.getId()), 0.0
            )

    def testRemoveComponentNotInLocation(self):
        '''Fail to remove a component that is not in the location.'''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        location = self.getLocation()
        with assert_raises(ftrack.LocationError):
            location.removeComponent(component.getId())

    def testRemoveComponentWithoutManagingData(self):
        '''Remove component from location without managing its data.'''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None,
            manageData=False
        )

        location = self.getLocation()
        componentInLocation = location.addComponent(
            component, manageData=False
        )

        # Explicitly add the data to the correct location. This is required
        # as some locations won't allow manageData=True when adding the
        # component.
        targetAccessor = location.getAccessor()
        targetStructure = location.getStructure()
        targetIdentifier = targetStructure.getResourceIdentifier(component)

        if not targetAccessor.exists(targetIdentifier):
            container = os.path.dirname(targetIdentifier)
            targetAccessor.makeContainer(container)

            sourceAccessor = component.getLocation().getAccessor()
            source = sourceAccessor.open(
                component.getResourceIdentifier(), 'rb'
            )
            target = targetAccessor.open(targetIdentifier, 'wb')
            target.write(source.read())
            target.close()
            source.close()

        ok_(
            location.getAccessor().exists(
                componentInLocation.getResourceIdentifier()
            ),
            'Data did not exist after component was added.'
        )

        componentId = componentInLocation.getId()

        # Ensure it is available in the location.
        assert_equal(location.getComponentAvailability(componentId), 100.0)

        # Remove component without managing data.
        location.removeComponent(componentId, manageData=False)

        # Ensure it is no longer available in the location.
        assert_equal(location.getComponentAvailability(componentId), 0.0)

        # Check data is still available and was not removed.
        ok_(
            location.getAccessor().exists(
                componentInLocation.getResourceIdentifier()
            ),
            'Data was removed despite manageData=False.'
        )

    def testGetComponentAvailability(self):
        '''Calculate component availability.'''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        location = self.getLocation()

        assert_equal(
            location.getComponentAvailability(component.getId()), 0.0
        )

        location.addComponent(component)

        assert_equal(
            location.getComponentAvailability(component.getId()), 100.0
        )

    def testGetComponentAvailabilityQuantization(self):
        '''Test for quantization errors when calculating availability.'''
        component = ftrack.createComponent(
            path='imageSequence.%04d.png [1-9]',
            location=None
        )
        componentId = component.getId()
        location = self.getLocation()

        location.addComponent(component, manageData=False)

        assert_equal(len(component.getMembers()), 9)
        assert_equal(location.getComponentAvailability(componentId), 100.0)

    def testSetGetResourceIdentifierTransformer(self):
        '''Set and retrieve resource identifier transformer.'''
        location = self.createRandomLocation()

        assert_equal(location.getResourceIdentifierTransformer(), None)

        mockTransformer = object()
        location.setResourceIdentifierTransformer(mockTransformer)
        assert_equal(
            location.getResourceIdentifierTransformer(), mockTransformer
        )

    def testResourceIdentifierTransformer(self):
        '''Round trip resource identifier transformer.'''
        location = self.getLocation()
        originalTransformer = location.getResourceIdentifierTransformer()

        try:
            location.setResourceIdentifierTransformer(MockTransformer())

            component = ftrack.createComponent(
                path=self.componentPath,
                location=None
            )
            componentInLocation = location.addComponent(component)

            targetResourceIdentifier = location.getStructure()\
                .getResourceIdentifier(component)

            # Check that the value stored is the encoded value.
            metadata = location._getComponentMetadata(component.getId())
            assert_equal(
                metadata['resourceIdentifier'],
                'TEST:{0}'.format(targetResourceIdentifier)
            )

            # Check that resource identifier set on returned component is the
            # decoded value.
            assert_equal(
                componentInLocation.getResourceIdentifier(),
                targetResourceIdentifier
            )
        finally:
            location.setResourceIdentifierTransformer(originalTransformer)


class TestLocation(BaseLocationTest):
    '''Test base location implementation.'''

    def getLocation(self):
        '''Return location instance to test against.'''
        return ftrack.Location('location_a')

    def testAddUnlocatedComponent(self):
        '''Fail to add component with no source location.'''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        component._setLocation(None)
        location = self.getLocation()

        with assert_raises(ftrack.LocationError):
            location.addComponent(component)

    def testAddComponentMissingSourceAccessor(self):
        '''Fail to add component where source location has no accessor.'''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        currentLocation = component.getLocation()
        currentAccessor = currentLocation.getAccessor()
        targetLocation = self.getLocation()

        try:
            currentLocation.setAccessor(None)
            with assert_raises(ftrack.LocationError):
                targetLocation.addComponent(component)
        finally:
            currentLocation.setAccessor(currentAccessor)


class MockTransformer(ftrack.ResourceIdentifierTransformer):
    '''Mock transformer.'''

    def encode(self, resourceIdentifier, context=None):
        '''Return encoded *resourceIdentifier*.'''
        return 'TEST:{0}'.format(resourceIdentifier)

    def decode(self, resourceIdentifier, context=None):
        '''Return decoded *resourceIdentifier*.'''
        return resourceIdentifier[5:]
