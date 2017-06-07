# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import platform as _platform
import os
from uuid import uuid4 as uuid

import ftrack
from .tools import assert_equal


class TestConnectStructure(object):
    '''Test connect structure.'''

    def setUp(self):
        '''Perform per test setup.'''
        self.assetPathPrefix = ftrack.getAssetPathPrefix()
        self.shotName = '010'
        self.assetName = 'my_asset_name'
        self.assetType = 'geo'

        workflow = ftrack.getProjectSchemes()[0]

        name = 'location-testproject-{0}'.format(uuid().hex)
        self.projectName = name
        self.project = ftrack.createProject(name, name, workflow)
        self.project.set('root', 'my_project_root_test')

        shot = self.project.createShot(self.shotName)
        self.asset = shot.createAsset(self.assetName, self.assetType)

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

    def _getDirectoryPath(self, version):
        '''Return path to directory for *version*.'''

        return os.path.join(
            self.diskPrefix,
            self.project.get('root'),
            self.assetPathPrefix,
            self.shotName,
            self.assetType,
            self.assetName,
            'v{0}'.format(
                str(version).zfill(3)
            )
        )

    def _getFileName(self, version, componentName):
        '''Return base file name from *version* and *componentName*.'''
        return '_'.join((
            self.projectName,
            self.shotName,
            self.assetType,
            self.assetName,
            'v{0}'.format(
                str(version).zfill(3)
            ),
            componentName
        ))

    def _publishVersion(self):
        '''Return a new published asset version.'''
        return self.asset.createVersion()

    def testGetResourceIdentifierForSequenceComponent(self):
        '''Test getResourceIdentifier for sequence component.'''
        structure = ftrack.ConnectStructure()

        componentName = 'main'
        fileName = 'test.%04d.EXT'
        sequenceIdentifier = '{0} [0-5]'.format(fileName)

        version = self._publishVersion()
        sequenceComponent = version.createComponent(
            componentName, sequenceIdentifier, location=None
        )

        expectedStructure = os.path.join(
            self._getDirectoryPath(
                version.get('version')
            ),
            '{0}.%04d.EXT'.format(
                self._getFileName(version.get('version'), componentName)
            )
        )

        assert_equal(
            structure.getResourceIdentifier(sequenceComponent),
            expectedStructure
        )

    def testGetResourceIdentifierForSequenceComponentMember(self):
        '''Test getResourceIdentifier for member of sequence component.'''
        structure = ftrack.ConnectStructure()

        componentName = 'main'

        version = self._publishVersion()
        sequenceComponent = version.createComponent(
            componentName, 'test.%04d.EXT [0-5]', location=None
        )
        member = sequenceComponent.getMembers()[-1]

        expectedStructure = os.path.join(
            self._getDirectoryPath(
                version.get('version')
            ),
            '{0}.0005.EXT'.format(
                self._getFileName(version.get('version'), componentName)
            )
        )

        assert_equal(
            structure.getResourceIdentifier(member),
            expectedStructure
        )

    def testGetResourceIdentifierForFileComponent(self):
        '''Test getResourceIdentifier for file component.'''
        structure = ftrack.ConnectStructure()

        componentName = 'mayafile'
        fileName = 'MyFile.mb'

        version = self._publishVersion()
        component = version.createComponent(
            componentName, fileName, location=None
        )

        expectedStructure = os.path.join(
            self._getDirectoryPath(
                version.get('version')
            ),
            '{0}.mb'.format(
                self._getFileName(version.get('version'), componentName)
            )
        )

        assert_equal(
            structure.getResourceIdentifier(component),
            expectedStructure
        )
