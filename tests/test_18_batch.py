from nose.tools import *
import ftrack
from ftrack import asc, desc, limit, order_by, filter_by
from uuid import uuid1 as uuid
import sys
import datetime
import ftestutil

class test_Types:
    

    def setUp(self):
        pass
    
    def tearDown(self):
        pass


    def test_1_create_and_verify(self):
        #create
        ftrack.suspendCreate()
        try:
            showfullname = ftrack.getUUID()
            showname = ftrack.getUUID()
            workflows = ftrack.getProjectSchemes()        
            seqname = ftrack.getUUID()
            shotname = ftrack.getUUID()
            categories = ftrack.getListCategories()
            
            ftrack.resetDebug()
            
            for i in range(1,2):
                show = ftrack.createShow(showfullname + str(i),showname + str(i),workflows[0])
                
                myList = show.createList('nameoflist',categories[0])
                
                #create sequence
                
                seq = show.createSequence(seqname)
                
                
                #create shot
                
                shot = seq.createShot(shotname)
                
                asset = shot.createAsset(name='test',assetType='dai')
                version = asset.createVersion()

        finally:
            ftrack.resumeCreate()
        
        totalRequests = ftrack.xmlServer.getTotalRequests()
        
        ok_(totalRequests == 1, 'Only one request was made')
        


        ftrack.suspendCreate()
        try:
            project = ftestutil.createProject()
            
            projectTasks = ftestutil.createTasks(project,2)
            
            sequence = project.createSequence(str(uuid()))
            
            sequenceTasks = ftestutil.createTasks(sequence,3)
            
            shot = sequence.createShot(str(uuid()))
            
            shotTasks = ftestutil.createTasks(shot,4)
        finally:
            ftrack.resumeCreate()

        #verify - length of tasks
        ok_(len(project.getTasks()) == 2, "project has 2 tasks")
        ok_(len(sequence.getTasks()) == 3, "project has 3 tasks")
        ok_(len(shot.getTasks()) == 4, "project has 4 tasks")
        
        
    def test_2_create_and_attribute(self):
        
        ftrack.suspendCreate()
        try:
            showfullname = ftrack.getUUID()
            showname = ftrack.getUUID()
            workflows = ftrack.getProjectSchemes()        
            seqname = ftrack.getUUID()
            shotname = ftrack.getUUID()
            categories = ftrack.getListCategories()
            
            ftrack.resetDebug()
            
            
            show = ftrack.createShow(showfullname,showname,workflows[0])
            
            myList = show.createList('nameoflist',categories[0])
            
            #create sequence
            seq = show.createSequence(seqname)
            
            
            #create shot
            
            shot = seq.createShot(shotname)
            
            asset = shot.createAsset(name='test',assetType='dai')
            version = asset.createVersion()
            
            #attributes
            version.set('versiontest',56.0)
        finally:
            ftrack.resumeCreate()
        
        totalRequests = ftrack.xmlServer.getTotalRequests()
        
        ok_(totalRequests == 1, 'Only one request was made')
        
        ok_(version.get('versiontest') == 56.0, 'Attribute was set')
        
        
        version.set('versiontest',55.0)
        ok_(version.get('versiontest') == 55.0, 'Attribute was set')
        
        
        
        
        
        