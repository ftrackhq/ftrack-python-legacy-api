from nose.tools import *
import ftrack
from ftrack import asc, desc, limit, order_by, filter_by
from uuid import uuid1 as uuid
import sys
import ftestutil

class test_Types:
    

    def setUp(self):
        self.globalName = 'nose_test'
    
    def tearDown(self):
        pass

    def test_create_asset_build(self):
        '''Create an asset build.'''
        project = ftestutil.createProject()

        project.createAssetBuild(
            'giant', ftrack.TaskType('Character')
        )
        project.createAssetBuild(
            'giant2', ftrack.TaskType('Character')
        )

        ok_(len(project.getAssetBuilds()) == 2, 'Must be two')

    def test_2_link(self):

        p = ftestutil.createProject()

        assetBuild1 = p.createAssetBuild('giant',ftrack.TaskType('Character'))
        assetBuild2 = p.createAssetBuild('giant2',ftrack.TaskType('Character'))

        shot1 = p.createShot('010')
        shot2 = p.createShot('020')

        assetBuild1.addSuccessor(shot1)
        shot2.addPredecessor(assetBuild2)
        shot2.addPredecessor(assetBuild1)


        ok_(len(assetBuild1.getSuccessors()) == 2,"must be two asset builds")

    def test_createTask(self):

        p = ftestutil.createProject()

        assetBuild1 = p.createAssetBuild('giant',ftrack.TaskType('Character'))

        assetBuild1.createTask('my task',ftrack.TaskType('Compositing'),ftrack.TaskStatus('Not started'))

    def test_create_without_type(self):

        p = ftestutil.createProject()

        assetBuild1 = p.createAssetBuild('giant')

    def testGetAssetBuildTypes(self):
        '''Get asset build types from project.'''
        project = ftrack.getProject('test')
        assetBuildTypes = project.getAssetBuildTypes()

        found = False
        for assetBuildType in assetBuildTypes:
            if assetBuildType.getName() == 'Character':
                found = True
        ok_(found, 'Found character asset build type.')
