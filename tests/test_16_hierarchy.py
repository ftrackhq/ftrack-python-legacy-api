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
        project = ftestutil.createProject()
        
        projectTasks = ftestutil.createTasks(project,2)
        
        sequence = project.createSequence(str(uuid()))
        
        sequenceTasks = ftestutil.createTasks(sequence,3)
        
        shot = sequence.createShot(str(uuid()))
        
        shotTasks = ftestutil.createTasks(shot,4)
        
        
        #verify - length of tasks
        ok_(len(project.getTasks()) == 2, "project has 2 tasks")
        ok_(len(sequence.getTasks()) == 3, "project has 3 tasks")
        ok_(len(shot.getTasks()) == 4, "project has 4 tasks")
        
        #verify - ids of tasks
        projectTaskIdsServer = sorted([task.getId() for task in project.getTasks()])
        projectTaskIdsLocal = sorted([task.getId() for task in projectTasks])
        ok_(projectTaskIdsServer == projectTaskIdsLocal, 'server is same as local for project')
        
        seqTaskIdsServer = sorted([task.getId() for task in sequence.getTasks()])
        seqTaskIdsLocal = sorted([task.getId() for task in sequenceTasks])
        ok_(seqTaskIdsServer == seqTaskIdsLocal, 'server is same as local for sequence')
        
        shotTaskIdsServer = sorted([task.getId() for task in shot.getTasks()])
        shotTaskIdsLocal = sorted([task.getId() for task in shotTasks])
        ok_(shotTaskIdsServer == shotTaskIdsLocal, 'server is same as local for shot')
        
        allIds = projectTaskIdsServer
        allIds.extend(seqTaskIdsServer)
        allIds.extend(shotTaskIdsServer)
        
        allTasks = project.getTasks(includeChildren=True)
        
        allTaskIdsLocal = sorted(allIds)
        allTaskIdsServer = sorted([task.getId() for task in allTasks])
        ok_(allTaskIdsLocal == allTaskIdsServer, 'server is same as local for all tasks')
        
        #verify - length of others
        ok_(len(project.getSequences()) == 1, "project has 1 sequences")
        ok_(len(sequence.getShots()) == 1, "project has 1 shot")
        
        ok_(len(project.getChildren()) == 1, "project has 2 items")
        ok_(len(sequence.getChildren()) == 1, "project has 1 shot")        
        
        #verify - ids of others
        ok_(sequence.getId() == project.getSequences()[0].getId(), 'server is same as local for sequence')
        ok_(shot.getId() == sequence.getShots()[0].getId(), 'server is same as local for shot')
        
        ok_(sequence.getId() in [project.getChildren()[0].getId(),project.getChildren()[0].getId()], 'server is same as local for sequence')
        ok_(shot.getId() == sequence.getChildren()[0].getId(), 'server is same as local for shot')
        
        #verify
        serverSequence = ftrack.getSequence([project.getName(),sequence.getName()])
        ok_(sequence.getId() == serverSequence.getId(), 'server is same as local for sequence')        
        
        serverShot = ftrack.getShot([project.getName(),sequence.getName(),shot.getName()])
        ok_(shot.getId() == serverShot.getId(), 'server is same as local for shot')
        
        
        