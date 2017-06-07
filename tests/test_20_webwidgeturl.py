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


    def test_1_getwidgeturl(self):
        
        name = "info"

        # project = ftrack.getProject('test')
        # url = project.getWebWidgetUrl(name)

        task = ftrack.Task('c410b0dc-6c58-11e1-8a63-f23c91df25eb')
        url = task.getWebWidgetUrl(name)

        #version
        version = ftrack.AssetVersion("1244503a-6766-11e1-b2ea-f23c91df25eb")
        version = version.getWebWidgetUrl(name)


    @raises(ftrack.FTrackError)
    def test_2_getwidgeturl_bad_name(self):
        
        name = None

        project = ftrack.getProject('test')
        url = project.getWebWidgetUrl(name)
        
        
    def testGetUrl(self):
        '''Retrieve the url from server and verify that it contains the id.'''
        taskId = 'c410b0dc-6c58-11e1-8a63-f23c91df25eb'
        task = ftrack.Task(taskId)
        url = task.getURL()
        expectedResult = (
            '/#slideEntityId=c410b0dc-6c58-11e1-8a63-f23c91df25eb&slideEntityType=task'
            '&view=tasks&itemId=projects'
            '&entityId=5671dcb0-66de-11e1-8e6e-f23c91df25eb&entityType=show'
        )
        ok_(url.find(expectedResult) != -1, 'Match with expected result.')      