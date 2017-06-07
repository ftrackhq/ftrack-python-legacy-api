from nose.tools import *
import ftrack
from ftrack import asc, desc, limit, order_by, filter_by
from uuid import uuid1 as uuid
import sys

class test_Types:
    

    def setUp(self):
        self.globalName = 'nose_test'
    
    def tearDown(self):
        pass

    def _createTask(self):
        #create show
        showfullname = ftrack.getUUID()
        showname = ftrack.getUUID()
        workflows = ftrack.getProjectSchemes()
        w = None
        #make sure we get vfx workflow
        for workflow in workflows:
            if workflow.getId() == '69cb7f92-4dbf-11e1-9902-f23c91df25eb':
                w = workflow
        show = ftrack.createShow(showfullname,showname,w)
        
        
        #create sequence
        seqname = ftrack.getUUID()
        seq = show.createSequence(seqname)
        
        
        #create shot
        shotname = ftrack.getUUID()
        shot = seq.createShot(shotname)      
        
        IN_PROGRESS_STATUS = '44ddd0fe-4164-11df-9218-0019bb4983d8'
        DONE_STATUS = '44de097a-4164-11df-9218-0019bb4983d8'
        modeling = '44dc53c8-4164-11df-9218-0019bb4983d8'
        
        taskName1 = str(uuid())
        task1 = shot.createTask(taskName1,ftrack.TaskType(modeling),ftrack.TaskStatus(IN_PROGRESS_STATUS))        
        
        return task1

    def test_1_default_recipients(self):
        task = self._createTask()
        
        suggested = task.getDefaultRecipients()
        
        ok_(len(suggested) == 0, '0 suggested recipients')
        
        user = ftrack.getUser('standard')
        
        task.assignUser(user)
        
        suggested = task.getDefaultRecipients()
        
        ok_(len(suggested) == 1, 'one suggested recipient')
        
        ok_(suggested[0].getId() == user.getId(), 'correct suggested recipient')
        
        
        categories = ftrack.getNoteCategories()

        note = task.createNote('note',categories[0])
        
        
        suggested = note.getDefaultRecipients()
        
        ok_(len(suggested) == 1, 'one suggested recipient')
        
        user2 = ftrack.getUser('root')
        suggested.append(user2)

        note2 = note.createNote('note',categories[0],recipients=suggested)
        
        recipients = note.getRecipients()
        
        ok_(len(recipients) == 1, 'one recipient')
        
        
        recipients = note2.getRecipients()
        
        ok_(len(recipients) == 2, 'two recipients')        
        
        userids = [user.getId() for user in recipients]
        
        ok_(user.getId() in userids, "Correct user1")
        ok_(user2.getId() in userids, "Correct user2")
        
        
        
        
        
        