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
    
    def test_1_tasktypes(self):
        
        def check(tasks):
            ok_(len(tasks) == 1, "Should be one task")
            ok_(tasks[0].getType().getName() == "Compositing", "Should be one task")
            
        shot = ftrack.getShotFromPath(['test','python_api','tasks'])
        compositing = ftrack.TaskType("44dd23b6-4164-11df-9218-0019bb4983d8")
        
        tasks = shot.getTasks(taskTypes=['Compositing'])
        check(tasks)
        
        tasks = shot.getTasks(taskTypes=[compositing])
        check(tasks)
        
        tasks = shot.getTasks(taskTypes=["44dd23b6-4164-11df-9218-0019bb4983d8"])
        check(tasks)
        
        
        
    def test_2_taskstatus(self):
        
        def check(tasks):
            ok_(len(tasks) == 4, "Should be four tasks")
            ok_(tasks[0].getStatus().getName() == "Not started", "Should be one task")
            
        shot = ftrack.getShotFromPath(['test','python_api','tasks'])
        notstarted = ftrack.TaskStatus("44dd9fb2-4164-11df-9218-0019bb4983d8")
        
        tasks = shot.getTasks(taskStatuses=['Not started'])
        check(tasks)
        
        tasks = shot.getTasks(taskStatuses=[notstarted])
        check(tasks)
        
        tasks = shot.getTasks(taskStatuses=["44dd9fb2-4164-11df-9218-0019bb4983d8"])
        check(tasks)
        
        
    def test_3_taskstates(self):
        
        def check(tasks):
            ok_(len(tasks) == 4, "Should be four tasks")
            ok_(tasks[0].getStatus().getName() == "Not started", "Should be one task")
            
        shot = ftrack.getShotFromPath(['test','python_api','tasks'])
        
        tasks = shot.getTasks(states=[ftrack.NOT_STARTED])
        check(tasks)
        
        
    def test_4_taskusers(self):
        
        def check(tasks):
            ok_(len(tasks) == 1, "Should be four tasks")
            ok_(tasks[0].getName() == "t1", "Should be t1")
            
        shot = ftrack.getShotFromPath(['test','python_api','tasks'])
        
        user = ftrack.User('jenkins')
        
        tasks = shot.getTasks(users=['jenkins'])
        check(tasks)
        
        tasks = shot.getTasks(users=[user])
        check(tasks)
        

    def test_5_usertypecombo(self):
        
        def check(tasks):
            ok_(len(tasks) == 1, "Should be four tasks")
            ok_(tasks[0].getName() == "t1", "Should be t1")
            
        shot = ftrack.getShotFromPath(['test','python_api','tasks'])
        
        user = ftrack.User('jenkins')
        
        tasks = shot.getTasks(users=['jenkins'],taskTypes=['44dd23b6-4164-11df-9218-0019bb4983d8'])
        check(tasks)

        
        tasks = shot.getTasks(users=['jenkins'],taskStatuses=['44ddd0fe-4164-11df-9218-0019bb4983d8'])
        check(tasks)

        tasks = shot.getTasks(users=['jenkins'],taskStatuses=['44ddd0fe-4164-11df-9218-0019bb4983d8'],taskTypes=['44dd23b6-4164-11df-9218-0019bb4983d8'])
        check(tasks)


    def test_6_includePath(self):
        
        def check(tasks):
            ok_(len(tasks) == 1, "Should be four tasks")
            ok_(tasks[0].getName() == "t1", "Should be t1")
            ok_(len(tasks[0].get('path')) == 4, "should be 4 items in the path")
            
        shot = ftrack.getShotFromPath(['test','python_api','tasks'])
        
        user = ftrack.User('jenkins')
        
        tasks = shot.getTasks(users=['jenkins'],taskTypes=['44dd23b6-4164-11df-9218-0019bb4983d8'],includePath=True)
        check(tasks)

    def test_7_projects(self):
        
        user = ftrack.User('jenkins')

        p1 = ftestutil.createProject()
        p2 = ftestutil.createProject()

        t1 = ftestutil.createTasks(p1)
        t2 = ftestutil.createTasks(p2)

        oldLen = len(user.getTasks())

        t1.assignUser(user)
        t2.assignUser(user)


        tasks = user.getTasks()
        ok_(len(tasks) == oldLen + 2, "must be more than 1")


        tasks = user.getTasks(projects=[p1])
        ok_(len(tasks) == 1, "must be 1")

        tasks = user.getTasks(projects=[p1,p2])
        ok_(len(tasks) == 2, "must be 2")

        p1.delete()
        p2.delete()





