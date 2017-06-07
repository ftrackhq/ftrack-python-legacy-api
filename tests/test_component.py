# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack

import os
import glob
from uuid import uuid4 as uuid

import clique
import ftrack

from .tools import ok_, assert_equal, assert_raises, assert_raises_regexp


class TestComponent(object):
    '''Test component API.'''

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
        self.sequenceComponentPath = self.sequenceCollection.format(
            '{head}{padding}{tail}'
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

    def testCreateComponent(self):
        '''Create a new component.'''
        component = ftrack.createComponent('main')
        ok_(isinstance(component, ftrack.Component))
        
    def testCreateComponentWithPath(self):
        '''Create a new component using a specific path.'''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        ok_(isinstance(component, ftrack.Component))
        assert_equal(component.getResourceIdentifier(), self.componentPath)

    def testCreateComponentWithSequencePath(self):
        '''Create a new component using a specific sequence path.'''
        component = ftrack.createComponent(
            path=self.sequenceComponentDescription,
            location=None
        )
        ok_(isinstance(component, ftrack.Component))
        assert_equal(component.isContainer(), True)
        assert_equal(component.getResourceIdentifier(), self.sequenceComponentPath)
        assert_equal(component.getPadding(), 3)

        members = component.getMembers()
        assert_equal(len(members), 5)
        assert_equal(members[0].getName(), '001')

    def testCreateComponentWithFile(self):
        '''Create a new component using deprecated file argument.'''
        component = ftrack.createComponent(
            file=self.componentPath,
            location=None
        )
        ok_(isinstance(component, ftrack.Component))
        assert_equal(component.getResourceIdentifier(), self.componentPath)

    def testCreateComponentWithFileAndPath(self):
        '''Create a new component using both file and path arguments.'''
        path = '/test/path.jpg'
        with assert_raises(TypeError):
            ftrack.createComponent('main', file=path, path=path)

    def testCreateComponentWithSystemType(self):
        '''Create a new component using specific system type.'''
        component = ftrack.createComponent(systemType=None)
        assert_equal(component.getSystemType(), 'file')

        component = ftrack.createComponent(systemType='file')
        assert_equal(component.getSystemType(), 'file')

        component = ftrack.createComponent(systemType='sequence')
        assert_equal(component.getSystemType(), 'sequence')

        with assert_raises(ftrack.FTrackError):
            ftrack.createComponent(systemType='invalid-type')

    def testCreateComponentWithMissingOriginLocation(self):
        '''Fail to create a component when origin location not available.'''
        origin = ftrack.LOCATION_PLUGINS.get('ftrack.origin')
        try:
            ftrack.LOCATION_PLUGINS.discard(origin)
            with assert_raises(ftrack.FTrackError):
                ftrack.createComponent()
        finally:
            ftrack.LOCATION_PLUGINS.add(origin)

    def testCreateComponentAttachedToVersion(self):
        '''Create a new component attached to a version.'''
        showName = 'show-{0}'.format(uuid().hex)
        show = ftrack.createShow(showName, showName,
                                 ftrack.ProjectScheme('VFX Scheme'))
        
        sequenceName = 'sequence-{0}'.format(uuid().hex)
        sequence = show.createSequence(sequenceName)
        
        asset = sequence.createAsset(name='monty', assetType='geo')
        version = asset.createVersion()
        
        component = version.createComponent('preview')
        ok_(isinstance(component, ftrack.Component))

        component = version.createComponent('model')
        ok_(isinstance(component, ftrack.Component))
    
    def testCreateComponentAttachedToVersionWithDuplicateName(self):
        '''Fail to create component with duplicate name attached to version.'''
        showName = 'show-{0}'.format(uuid().hex)
        show = ftrack.createShow(showName, showName,
                                 ftrack.ProjectScheme('VFX Scheme'))
        
        sequenceName = 'sequence-{0}'.format(uuid().hex)
        sequence = show.createSequence(sequenceName)
        
        asset = sequence.createAsset(name='monty', assetType='geo')
        version = asset.createVersion()
        
        component = version.createComponent('preview')
        ok_(isinstance(component, ftrack.Component))
        
        with assert_raises_regexp(
            ftrack.FTrackError,
            'Component with that name already exists'
        ):
            component = version.createComponent('preview')
        
    def testIsContainer(self):
        '''Check whether component is a container.'''
        component = ftrack.createComponent('model')
        assert_equal(component.isContainer(), False)
        
        component = ftrack.createComponent('model', systemType='sequence')
        assert_equal(component.isContainer(), True)
        
    def testGetMembers(self):
        '''Retrieve container members.'''
        component = ftrack.createComponent('preview', systemType='sequence')
        assert_equal(component.getMembers(), [])

    def testGetMembersOfNonContainer(self):
        '''Fail to retrieve members of non-container.'''
        component = ftrack.createComponent('model')
        with assert_raises_regexp(TypeError, 'Component is not a container.'):
            component.getMembers()

    def testGetMembersInLocation(self):
        '''Retrieve container members in specific valid location.'''
        location = ftrack.LOCATION_PLUGINS.get('location_a')
        component = ftrack.createComponent(
            path=self.sequenceComponentDescription,
            location=location
        )

        members = component.getMembers(location=location)
        for member in members:
            assert_equal(member.getLocation().getId(), location.getId())

    def testGetMembersInInvalidLocation(self):
        '''Retrieve container members in specific invalid location.'''
        component = ftrack.createComponent(
            path=self.sequenceComponentDescription,
            location=None
        )
        location = ftrack.LOCATION_PLUGINS.get('location_b')

        with assert_raises(ftrack.LocationError):
            component.getMembers(location=location)

    def testGetMembersInAutoLocation(self):
        '''Retrieve members in auto location when in container location.'''
        location = ftrack.LOCATION_PLUGINS.get('location_a')
        component = ftrack.createComponent(
            path=self.sequenceComponentDescription,
            location=location
        )

        members = component.getMembers(location='auto')
        for member in members:
            assert_equal(member.getLocation().getId(), location.getId())

    def testGetMembersInAutoLocationWhenNotInContainerLocation(self):
        '''Retrieve members in auto location when not in container location.'''
        component = ftrack.createComponent(
            path=self.sequenceComponentDescription,
            location=None
        )
        location = ftrack.LOCATION_PLUGINS.get('location_a')
        componentInLocation = location.addComponent(component, recursive=False)

        members = componentInLocation.getMembers(location='auto')
        for member in members:
            assert_equal(member.getLocation(), None)

    def testAddMember(self):
        '''Add member to container.'''
        component = ftrack.createComponent('preview', systemType='sequence')
        assert_equal(len(component.getMembers()), 0)
        
        member = ftrack.createComponent('0001')
        component.addMember(member)

        members = component.getMembers()
        assert_equal(len(members), 1)
        assert_equal(members[0].getId(), member.getId())
    
    def testAddMemberToNonContainer(self):
        '''Fail to add member to non-container.'''
        component = ftrack.createComponent('model')
        member = ftrack.createComponent('0001')
        
        with assert_raises_regexp(TypeError,
                                  'Cannot add member to non-container.'):
            component.addMember(member)
    
    def testAddMemberToDifferentContainer(self):
        '''Fail to add component to a different container.'''
        container_a = ftrack.createComponent('a', systemType='sequence')
        container_b = ftrack.createComponent('b', systemType='sequence')
        
        member = ftrack.createComponent('0001')
        container_a.addMember(member)
        
        with assert_raises_regexp(
            ftrack.FTrackError,
            'Component cannot be a member of multiple containers'
        ):
            container_b.addMember(member)
    
    def testRemoveMemberFromContainer(self):
        '''Remove member component from its container.'''
        container = ftrack.createComponent('a', systemType='sequence')
        member = ftrack.createComponent('0001')
        container.addMember(member)

        assert_equal(len(container.getMembers()), 1)

        container.removeMember(member)
        
        assert_equal(len(container.getMembers()), 0)

    def testRemoveMemberFromNonContainer(self):
        '''Fail to remove member from non-container.'''
        component = ftrack.createComponent('model')
        member = ftrack.createComponent('0001')

        with assert_raises_regexp(
                TypeError,
                'Cannot remove member from non-container.'
        ):
            component.removeMember(member)

    def testRemoveNonMemberFromContainer(self):
        '''Fail to remove component that is not a member of any container.'''
        container = ftrack.createComponent('a', systemType='sequence')
        component = ftrack.createComponent('0001')
        
        with assert_raises_regexp(
            ftrack.FTrackError, 
            'Component is not a member of any container.'
        ):
            container.removeMember(component)
        
    def testRemoveMemberOfDifferentContainerFromContainer(self):
        '''Fail to remove component that is a member of a different container.'''
        container_a = ftrack.createComponent('a', systemType='sequence')
        container_b = ftrack.createComponent('b', systemType='sequence')
        member = ftrack.createComponent('0001')
        
        container_a.addMember(member)
        
        with assert_raises_regexp(
            ftrack.FTrackError, 
            'Component is not a member of this container.'
        ):
            container_b.removeMember(member)
        
    def testGetVersion(self):
        '''Retrieve associated version via component.'''
        showName = 'show-{0}'.format(uuid().hex)
        show = ftrack.createShow(showName, showName,
                                 ftrack.ProjectScheme('VFX Scheme'))

        sequenceName = 'sequence-{0}'.format(uuid().hex)
        sequence = show.createSequence(sequenceName)

        asset = sequence.createAsset(name='monty', assetType='geo')
        version = asset.createVersion()

        component = version.createComponent()
        ok_(isinstance(component, ftrack.Component))

        retrievedVersion = component.getVersion()
        assert_equal(version.getId(), retrievedVersion.getId())

    def testGetVersionWhenUndefined(self):
        '''Fail to retrieve version via component when none associated.'''
        component = ftrack.createComponent()
        ok_(component.getVersion() is None)

    def testGetContainer(self):
        '''Return container of component.'''
        component = ftrack.createComponent(systemType='sequence')
        member = ftrack.createComponent('0001')
        component.addMember(member)

        assert_equal(
            member.getContainer().getId(), component.getId()
        )

    def testGetContainerInLocation(self):
        '''Retrieve container in specific valid location.'''
        location = ftrack.LOCATION_PLUGINS.get('location_a')
        component = ftrack.createComponent(
            path=self.sequenceComponentDescription,
            location=location
        )

        members = component.getMembers()
        member = members[0]
        assert_equal(member.getLocation().getId(), location.getId())

        container = member.getContainer(location=location)
        assert_equal(container.getLocation().getId(), location.getId())

    def testGetContainerInInvalidLocation(self):
        '''Retrieve container in specific invalid location.'''
        component = ftrack.createComponent(
            path=self.sequenceComponentDescription,
            location=None
        )
        location = ftrack.LOCATION_PLUGINS.get('location_b')

        members = component.getMembers()
        member = members[0]

        with assert_raises(ftrack.LocationError):
            member.getContainer(location=location)

    def testGetContainerInAutoLocation(self):
        '''Retrieve container in auto location when in member location.'''
        location = ftrack.LOCATION_PLUGINS.get('location_a')
        component = ftrack.createComponent(
            path=self.sequenceComponentDescription,
            location=location
        )

        members = component.getMembers()
        member = members[0]
        assert_equal(member.getLocation().getId(), location.getId())

        container = member.getContainer(location='auto')
        assert_equal(container.getLocation().getId(), location.getId())

    def testGetContainerInAutoLocationWhenNotInMemberLocation(self):
        '''Retrieve container in auto location when not in member location.'''
        component = ftrack.createComponent(
            path=self.sequenceComponentDescription,
            location=None
        )
        location = ftrack.LOCATION_PLUGINS.get('location_a')
        members = component.getMembers()
        member = members[0]

        memberInLocation = location.addComponent(member)

        container = memberInLocation.getContainer(location='auto')
        assert_equal(container.getLocation(), None)

    def testGetContainerWhenNotContained(self):
        '''Fail to return container when component not contained.'''
        member = ftrack.createComponent('0001')
        ok_(member.getContainer() is None)

    def testGetName(self):
        '''Return component name.'''
        component = ftrack.createComponent('main')
        assert_equal(component.getName(), 'main')

    def testGetImportPath(self):
        '''Return import path (now access path).'''
        component = ftrack.createComponent()
        assert_equal(component.getImportPath(), None)

        component = ftrack.createComponent(
            path=self.componentPath
        )
        assert_equal(component.getImportPath(), component.getFilesystemPath())

    def testGetFile(self):
        '''Return file path (now internal path).'''
        component = ftrack.createComponent()
        assert_equal(component.getFile(), None)

        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        assert_equal(component.getFile(), component.getResourceIdentifier())

    def testGetFileType(self):
        '''Return component file type.'''
        component = ftrack.createComponent()
        assert_equal(component.getFileType(), '')

        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        assert_equal(component.getFileType(), '.jpg')

    def testGetFilesystemPath(self):
        '''Return filesystem path from origin location.'''
        component = ftrack.createComponent()
        assert_equal(component.getFilesystemPath(), None)

        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        assert_equal(component.getFilesystemPath(), self.componentPath)

    def testGetFilesystemPathFromSpecificLocation(self):
        '''Return filesystem path from specific location.'''
        component = ftrack.createComponent()
        assert_equal(component.getFilesystemPath(), None)

        location = ftrack.LOCATION_PLUGINS.get('location_a')
        accessor = location.getAccessor()

        component = ftrack.createComponent(
            path=self.componentPath,
            location=location
        )

        filesystemPath = accessor.getFilesystemPath(
            component.getResourceIdentifier()
        )
        assert_equal(component.getFilesystemPath(), filesystemPath)

    def testGetResourceIdentifier(self):
        '''Return internal path.'''
        component = ftrack.createComponent()
        assert_equal(component.getResourceIdentifier(), None)

        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        assert_equal(component.getResourceIdentifier(), self.componentPath)

    def testSetResourceIdentifier(self):
        '''Set internal path.'''
        component = ftrack.createComponent()
        assert_equal(component.getResourceIdentifier(), None)
        component.setResourceIdentifier(self.componentPath)
        assert_equal(component.getResourceIdentifier(), self.componentPath)

    def testGetLocation(self):
        '''Return current component location.'''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )
        assert_equal(
            component.getLocation().getId(),
            ftrack.LOCATION_PLUGINS.get('ftrack.origin').getId()
        )

        component = ftrack.createComponent()
        assert_equal(component.getLocation(), None)

    def testSetLocation(self):
        '''Set current component location.'''
        component = ftrack.createComponent()
        assert_equal(component.getLocation(), None)

        origin = ftrack.LOCATION_PLUGINS.get('ftrack.origin')
        component._setLocation(origin)
        assert_equal(component.getLocation().getId(), origin.getId())

    def testSwitchToLocation(self):
        '''Switch to specific location for component.'''
        locationA = ftrack.LOCATION_PLUGINS.get('location_a')
        component = ftrack.createComponent(
            path=self.componentPath,
            location=locationA
        )

        retrievedComponent = ftrack.Component(
            component.getId(),
            location=None
        )
        assert_equal(retrievedComponent.getLocation(), None)
        assert_equal(retrievedComponent.getResourceIdentifier(), None)

        retrievedComponent.switchLocation(locationA)

        assert_equal(
            retrievedComponent.getLocation().getId(),
            locationA.getId()
        )

        assert_equal(
            component.getResourceIdentifier(),
            retrievedComponent.getResourceIdentifier()
        )

    def testSwitchToInvalidLocation(self):
        '''Fail to switch to location where component is not available.

        Should raise LocationError.

        '''
        locationB = ftrack.LOCATION_PLUGINS.get('location_b')
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )

        with assert_raises(ftrack.LocationError):
            component.switchLocation(locationB)

    def testSwitchToAutoLocation(self):
        '''Switch to automatically determined location for component.'''
        locationA = ftrack.LOCATION_PLUGINS.get('location_a')
        component = ftrack.createComponent(
            path=self.componentPath,
            location=locationA
        )

        retrievedComponent = ftrack.Component(
            component.getId(),
            location=None
        )
        assert_equal(retrievedComponent.getLocation(), None)
        assert_equal(retrievedComponent.getResourceIdentifier(), None)

        retrievedComponent.switchLocation('auto')

        assert_equal(
            retrievedComponent.getLocation().getId(),
            locationA.getId()
        )

        assert_equal(
            component.getResourceIdentifier(),
            retrievedComponent.getResourceIdentifier()
        )

    def testSwitchToNoLocation(self):
        '''Switch to no location for component.'''
        locationA = ftrack.LOCATION_PLUGINS.get('location_a')
        component = ftrack.createComponent(
            path=self.componentPath,
            location=locationA
        )

        assert_equal(
            component.getLocation().getId(),
            locationA.getId()
        )

        ok_(
            component.getResourceIdentifier() is not None,
            'Component internal path was not set.'
        )

        component.switchLocation(None)

        assert_equal(component.getLocation(), None)
        assert_equal(component.getResourceIdentifier(), None)

    def testInitialiseWithAutoLocationAndNoLocationsAvailable(self):
        '''Initialise using 'auto' location when no locations available.'''
        component = ftrack.createComponent(
            path=self.componentPath, location=None
        )

        retrievedComponent = ftrack.Component(
            component.getId(),
            location='auto'
        )

        assert_equal(retrievedComponent.getLocation(), None)

    def testInitialiseWithAutoLocationAndLocationsAvailable(self):
        '''Initialise using 'auto' location when locations available.'''
        locationA = ftrack.LOCATION_PLUGINS.get('location_a')
        component = ftrack.createComponent(
            path=self.componentPath,
            location=locationA
        )

        retrievedComponent = ftrack.Component(
            component.getId(),
            location='auto'
        )

        assert_equal(
            retrievedComponent.getLocation().getId(),
            locationA.getId()
        )

    def testInitialiseComponentManually(self):
        '''Initialise component manually.'''
        component = ftrack.createComponent()

        retrievedComponent = ftrack.Component(
            component.getId(),
            resourceIdentifier=self.componentPath,
            location=None
        )
        assert_equal(retrievedComponent.getId(), component.getId())
        assert_equal(
            retrievedComponent.getResourceIdentifier(), self.componentPath
        )
        assert_equal(retrievedComponent.getFilesystemPath(), None)
        assert_equal(retrievedComponent.getLocation(), None)

    def testInitialiseComponentWithValidLocation(self):
        '''Initialise component with specific valid location.'''
        locationA = ftrack.LOCATION_PLUGINS.get('location_a')
        component = ftrack.createComponent(
            path=self.componentPath,
            location=locationA
        )

        retrievedComponent = ftrack.Component(
            component.getId(),
            location=locationA
        )

        assert_equal(
            retrievedComponent.getLocation().getId(),
            locationA.getId()
        )

    def testInitialiseComponentWithInvalidLocation(self):
        '''Initialise component with specific invalid location.'''
        locationA = ftrack.LOCATION_PLUGINS.get('location_a')
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )

        with assert_raises(ftrack.LocationError):
            ftrack.Component(
                component.getId(),
                location=locationA
            )

    def testInitialiseWithLocationAndPath(self):
        '''Initialise component with location and paths.

        The values should be set explicitly bypassing the switchLocation logic.

        '''
        locationA = ftrack.LOCATION_PLUGINS.get('location_a')
        explicitPath = '/random/invalid/path'

        component = ftrack.createComponent(
            path=self.componentPath,
            location=locationA
        )

        component = ftrack.Component(
            component.getId(),
            resourceIdentifier=explicitPath,
            location=locationA
        )

        assert_equal(component.getLocation().getId(), locationA.getId())
        assert_equal(component.getResourceIdentifier(), explicitPath)

    def testGetAvailability(self):
        '''Retrieve component availability.'''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )

        expected = {}
        for location in ftrack.getLocations():
            expected[location.getId()] = 0.0

        assert_equal(component.getAvailability(), expected)

    def testCreateComponentWithLocation(self):
        '''Create component with specific location.'''
        location = ftrack.LOCATION_PLUGINS.get('location_a')

        component = ftrack.createComponent(
            path=self.componentPath,
            location=location
        )

        assert_equal(component.getLocation().getId(), location.getId())

        try:
            location.getComponent(component.getId())
        except ftrack.LocationError:
            raise AssertionError('Component does not exist in location_a')

    def testCreateComponentWithoutLocation(self):
        '''Create component without specifying location.

        The component should be added to the ftrack.origin location

        '''
        component = ftrack.createComponent(
            path=self.componentPath,
            location=None
        )

        origin = ftrack.LOCATION_PLUGINS.get('ftrack.origin')
        assert_equal(component.getLocation().getId(), origin.getId())

    def testCreateComponentWithLocationMissingAccessor(self):
        '''Fail to create Component with location missing accessor.

        If manageData is True.

        '''
        invalidLocation = ftrack.LOCATION_PLUGINS.get(
            'location_without_accessor'
        )

        version = self._generateRandomVersion()

        with assert_raises_regexp(
            ftrack.LocationError, 'No accessor defined for location.'
        ):
            version.createComponent(
                path=self.componentPath,
                location=invalidLocation,
                manageData=True
            )

        assert_equal(len(version.getComponents()), 0)

    def testCreateComponentWithLocationMissingStructure(self):
        '''Fail to create Component with location missing structure.'''
        invalidLocation = ftrack.LOCATION_PLUGINS.get(
            'location_without_structure'
        )

        version = self._generateRandomVersion()

        with assert_raises_regexp(
            ftrack.LocationError, 'No structure defined for location.'
        ):
            version.createComponent(
                path=self.componentPath,
                location=invalidLocation
            )

        assert_equal(len(version.getComponents()), 0)

    def testCreateComponentWithLocationWithoutPath(self):
        '''Create Component when specifying location but no path.

        Component should not be added to location.

        '''
        location = ftrack.LOCATION_PLUGINS.get('location_a')

        component = ftrack.createComponent(
            location=location
        )

        assert_equal(component.getLocation(), None)

    def _assertReviewComponent(self, componentName, location='auto',
                               expectedLocation=None):
        '''Util to create a component and validate the correct location.'''
        component = ftrack.createComponent(
            name=componentName,
            path=self.componentPath,
            location=location
        )

        assert_equal(component.getLocation().getId(), expectedLocation.getId())

    def testCreateMp4ReviewComponentWithAuto(self):
        '''Create mp4 review component.

        Should be added to ftrack.review location.

        '''
        self._assertReviewComponent(
            'ftrackreview-mp4',
            expectedLocation=ftrack.Location('ftrack.review')
        )

    def testCreateWebmReviewComponentWithAuto(self):
        '''Create webm review component.

        Should be added to ftrack.review location.

        '''
        self._assertReviewComponent(
            'ftrackreview-webm',
            expectedLocation=ftrack.Location('ftrack.review')
        )

    def testCreateImageReviewComponentWithAuto(self):
        '''Create image review component.

        Should be added to ftrack.review location.

        '''
        self._assertReviewComponent(
            'ftrackreview-image',
            expectedLocation=ftrack.Location('ftrack.review')
        )

    def testCreateReviewComponentWithoutAuto(self):
        '''Create mp4 review component with specified location.

        Should be added to location_a location.

        '''
        self._assertReviewComponent(
            'ftrackreview-mp4',
            location=ftrack.Location('location_a'),
            expectedLocation=ftrack.Location('location_a')
        )

    def testCreateSequenceComponentWithSpecificPadding(self):
        '''Create a new sequence component with specific padding value.'''
        component = ftrack.createComponent(
            systemType='sequence',
            padding=4,
            location=None
        )
        ok_(isinstance(component, ftrack.Component))
        assert_equal(component.getPadding(), 4)

    def testCreateNonSequenceComponentWithSpecificPadding(self):
        '''Fail to create non-sequence component with specific padding value.'''
        with assert_raises_regexp(
            ftrack.FTrackError,
            'Cannot set padding attribute on non-sequence'
        ):
            ftrack.createComponent(
                systemType='file',
                padding=4,
                location=None
            )

    def testIsSequence(self):
        '''Return whether component is a sequence.'''
        component = ftrack.createComponent(systemType='file')
        assert_equal(component.isSequence(), False)

        component = ftrack.createComponent(systemType='sequence')
        assert_equal(component.isSequence(), True)

    def testGetPadding(self):
        '''Return padding for sequence.'''
        component = ftrack.createComponent(systemType='sequence')
        assert_equal(component.getPadding(), 0)

        component = ftrack.createComponent(systemType='sequence', padding=4)
        assert_equal(component.getPadding(), 4)

    def testSetPadding(self):
        '''Set padding value for sequence.'''
        component = ftrack.createComponent(systemType='sequence')
        assert_equal(component.getPadding(), 0)

        component.setPadding(4)
        assert_equal(component.getPadding(), 4)

    def testSetPaddingOnNonSequence(self):
        '''Fail to set padding on non-sequence.'''
        component = ftrack.createComponent(systemType='file')

        with assert_raises_regexp(TypeError, 'Component is not a sequence.'):
            component.setPadding(4)

    def testAvailabilityWithoutAllLocations(self):
        '''Return correct availbility without access to all locations.'''
        locationA = ftrack.LOCATION_PLUGINS.get('location_a')
        component = ftrack.createComponent(
            path=self.sequenceComponentDescription,
            location=locationA
        )

        locations = list(ftrack.LOCATION_PLUGINS)
        locations.remove(locationA)

        availability = component.getAvailability(
            locationIds=[
                location.getId() for location in locations
            ]
        )

        for location in locations:
            assert_equal(availability[location.getId()], 0)

        assert_equal(availability.get(locationA.getId()), None)
