# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack

from uuid import uuid1 as uuid

import ftrack

from .tools import ok_, raises



class test_Types:

    def __init__(self):
        '''Initialise test.'''
        self.globalName = 'nose_test'

    def test_1_remove(self):
        
        #create show
        showfullname = ftrack.getUUID()
        showname = ftrack.getUUID()
        workflows = ftrack.getProjectSchemes()
        show = ftrack.createShow(showfullname,showname,workflows[0])
        
        
        #create sequence
        seqname = ftrack.getUUID()
        seq = show.createSequence(seqname)
        
        
        #create shot
        shotname = ftrack.getUUID()
        shot = seq.createShot(shotname)
        
        
        asset = shot.createAsset(name='test',assetType='dai')
        version = asset.createVersion()

        quicktimeComponent = version.createComponent()

        #Export
        asset.publish()        
        
        #create tasks
        taskType = show.getTaskTypes()[0]
        taskStatus = show.getTaskStatuses()[0]
        task = None
        for i in range(1,6):
            taskname = ftrack.getUUID()
            task = shot.createTask(taskname,taskType,taskStatus)
        
        taskLength = len(shot.getTasks())
        #assign to task
        user = ftrack.User('standard')
        task.assignUser(user)
        
        
        #delete a task
        task = shot.getTasks()[0]
        
        task.delete()
        
        ok_(len(shot.getTasks()) == taskLength - 1, 'task was removed')
        
        shotid = shot.getId()
        shot.delete()
        
        try:
            ftrack.Shot(shotid)
            ok_(False,'was not removed')
        except ftrack.FTrackError:
            ok_(True,'was removed')        
        
        showid = show.getId()
        show.delete()
        
        try:
            ftrack.Show(showid)
            ok_(False,'was not removed')
        except ftrack.FTrackError:
            ok_(True,'was removed')
        
        
        
    def test_2_remove_asset_component(self):
        
        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        myTask = myShot.getTasks()[0]
        assetName = str(uuid())
        asset = myShot.createAsset(name=assetName,assetType='dai',task=myTask)
        version = asset.createVersion(taskid=myTask.getId())

        quicktimeComponent = version.createComponent()

        #Export
        asset.publish()
        
        
        quicktimeComponent.delete()
        asset.delete()
        
    def test_2_remove_asset_version(self):
        
        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        myTask = myShot.getTasks()[0]
        assetName = str(uuid())
        asset = myShot.createAsset(name=assetName,assetType='dai',task=myTask)
        version = asset.createVersion(taskid=myTask.getId())

        quicktimeComponent = version.createComponent()
    
        #Export
        asset.publish()
        
        
        version.delete()
        asset.delete()
        
    def test_3_remove_asset(self):
        
        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        myTask = myShot.getTasks()[0]
        assetName = str(uuid())
        asset = myShot.createAsset(name=assetName,assetType='dai',task=myTask)
        version = asset.createVersion(taskid=myTask.getId())

        quicktimeComponent = version.createComponent()
    
        #Export
        asset.publish()
        
        
        asset.delete() 

    @raises(ftrack.FTrackError)
    def test_4_remove_workflow(self):
        workflows = ftrack.getProjectSchemes()

        workflows[0].delete()
