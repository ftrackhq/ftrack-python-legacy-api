# :coding: utf-8
# :copyright: Copyright (c) 2016 ftrack

from uuid import uuid4 as uuid

import ftrack
from .tools import assert_equal


class TestStandardStructure(object):
    '''Test standard structure.'''

    def setUp(self):
        '''Perform per test setup.'''
        workflow = ftrack.getProjectSchemes()[0]

        name = 'location-testproject-{0}'.format(uuid().hex)
        self.projectName = name
        self.project = ftrack.createProject(name, name, workflow)
        self.project.set('root', 'my_project_root_test')

        self.fileComponentNonAsciiName = newFileComponent(name=u'fää')
        self.fileComponentIllegalName = newFileComponent(name=u'fo/o')
        self.fileComponent = newFileComponent()
        self.sequenceComponent = newSequenceComponent()
        self.sequenceComponentMember = self.sequenceComponent.getMembers()[3]


def newSequenceComponent():
    '''Return sequence component.'''
    entity = ftrack.createComponent(
        'baz', '/tmp/foo/%04d.jpg [1-10]', location=None
    )

    return entity


def newFileComponent(name='foo'):
    '''Return file component with *name* .'''
    entity = ftrack.createComponent(
        name,
        '/path/to/file.png',
        location=None
    )

    return entity


def createMethod(
    testName, testDocstring, componentAttribute, hierarchy, expected, structure,
    assetName
):
    '''Return new test.'''
    def wrappedTest(self):
        parent = self.project
        for name in hierarchy:
            parent = parent.create('Folder', name)

        asset = parent.createAsset(assetName, assetType='geo')
        versions = asset.getVersions()

        if versions:
            version = versions[0]
        else:
            version = asset.createVersion()

        component = getattr(self, componentAttribute)
        if component.getContainer():
            component.getContainer().set('version_id', version.getId())
        else:
            component.set('version_id', version.getId())

        print expected
        assert_equal(
            structure.getResourceIdentifier(component),
            expected.format(project_name=self.project.getName())
        )

    wrappedTest.__name__ = testName
    wrappedTest.__doc__ = testDocstring

    return wrappedTest

for testId, componentAttribute, hierarchy, expected, structure, assetName in [
    (
        'file_component_on_project',
        'fileComponent',
        [],
        '{project_name}/my_new_asset/v001/foo.png',
        ftrack.StandardStructure(),
        'my_new_asset'
    ),
    (
        'file_component_on_project_with_prefix',
        'fileComponent',
        [],
        '{project_name}/foobar/my_new_asset/v001/foo.png',
        ftrack.StandardStructure(
            projectVersionsPrefix='foobar'
        ),
        'my_new_asset'
    ),
    (
        'file_component_with_hierarchy',
        'fileComponent',
        ['baz1', 'bar'],
        '{project_name}/baz1/bar/my_new_asset/v001/foo.png',
        ftrack.StandardStructure(),
        'my_new_asset'
    ),
    (
        'sequence_component',
        'sequenceComponent',
        ['baz2', 'bar'],
        '{project_name}/baz2/bar/my_new_asset/v001/baz.%04d.jpg',
        ftrack.StandardStructure(),
        'my_new_asset'
    ),
    (
        'sequence_component_member',
        'sequenceComponentMember',
        ['baz3', 'bar'],
        '{project_name}/baz3/bar/my_new_asset/v001/baz.0004.jpg',
        ftrack.StandardStructure(),
        'my_new_asset'
    ),
    (
        'slugify_non_ascii_hierarchy',
        'fileComponent',
        [u'björn'],
        '{project_name}/bjorn/my_new_asset/v001/foo.png',
        ftrack.StandardStructure(),
        'my_new_asset'
    ),
    (
        'slugify_illegal_hierarchy',
        'fileComponent',
        [u'björn!'],
        '{project_name}/bjorn_/my_new_asset/v001/foo.png',
        ftrack.StandardStructure(),
        'my_new_asset'
    ),
    (
        'slugify_non_ascii_component_name',
        'fileComponentNonAsciiName',
        [],
        '{project_name}/my_new_asset/v001/faa.png',
        ftrack.StandardStructure(),
        'my_new_asset'
    ),
    (
        'slugify_illegal_component_name',
        'fileComponentIllegalName',
        [],
        '{project_name}/my_new_asset/v001/fo_o.png',
        ftrack.StandardStructure(),
        'my_new_asset'
    ),
    (
        'slugify_non_ascii_asset_name',
        'fileComponent',
        [],
        '{project_name}/aao/v001/foo.png',
        ftrack.StandardStructure(),
        u'åäö'
    ),
    (
        'slugify_illegal_asset_name',
        'fileComponent',
        [],
        '{project_name}/my_ne____w_asset/v001/foo.png',
        ftrack.StandardStructure(),
        u'my_ne!!!!w_asset'
    ),
    (
        'slugify_none',
        'fileComponent',
        [u'björn2'],
        u'{project_name}/björn2/my_new_asset/v001/foo.png',
        ftrack.StandardStructure(
            illegalCharacterSubstitute=None
        ),
        'my_new_asset'
    ),
    (
        'slugify_other_character',
        'fileComponent',
        [u'bj!rn'],
        '{project_name}/bj^rn/my_new_asset/v001/foo.png',
        ftrack.StandardStructure(
            illegalCharacterSubstitute='^'
        ),
        'my_new_asset'
    )
]:
    testName = 'test' + ''.join([name.title() for name in testId.split('_')])
    testDocstring = 'Test ' + testId.replace('_', ' ')
    setattr(
        TestStandardStructure,
        testName,
        createMethod(
            testName, testDocstring, componentAttribute, hierarchy, expected,
            structure, assetName
        )
    )
