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


    def test_1_roles(self):
        user = ftrack.User('standard')
        
        ok_(user.getUsername() == 'standard')
        
        
        roles = user.getRoles()
        
        ok_(roles[0].getName() == 'User')
        
               
    def test_2_getuser(self):
        
        user = ftrack.getUser('standard')
        
        ok_(user.getUsername() == 'standard')
        
        user = ftrack.getUser('standardasd')
        
        ok_(user == None)
        
        
    def test_3_gettasks(self):
        
        def createShot():
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
            
            return shot      
        
        shot = createShot()
        user = ftrack.getUser('standard')
        
        tasks = user.getTasks()
        originalNumberOfTasks = len(tasks)
        
        IN_PROGRESS_STATUS = '44ddd0fe-4164-11df-9218-0019bb4983d8'
        DONE_STATUS = '44de097a-4164-11df-9218-0019bb4983d8'
        modeling = '44dc53c8-4164-11df-9218-0019bb4983d8'
        
        taskName1 = str(uuid())
        taskName2 = str(uuid())
        task1 = shot.createTask(taskName1,ftrack.TaskType(modeling),ftrack.TaskStatus(IN_PROGRESS_STATUS))
        task2 = shot.createTask(taskName2,ftrack.TaskType(modeling),ftrack.TaskStatus(DONE_STATUS))
        
        task1.assignUser(user)
        task2.assignUser(user)
        
        ok_(len(user.getTasks()) == originalNumberOfTasks+2, 'Two more tasks on user')
        
        
        #query using STATE
        tasks = user.getTasks(states=[ftrack.NOT_STARTED,ftrack.IN_PROGRESS])
        
        foundInProgress = False
        foundDone = False
        
        for t in tasks:
            if t.getStatus() == ftrack.IN_PROGRESS:
                foundInProgress = True
            if t.getStatus() == ftrack.DONE:
                foundDone = True                
            
        ok_(foundInProgress,'In progress task was found')
        ok_(foundDone == False,'Done task was not found')
        
        
        #query using TYPE
        tasks = user.getTasks(taskTypes=[modeling])
        
        foundModeling = False
        foundOther = False
        
        for t in tasks:
            if t.get('typeid') == modeling:
                foundModeling = True
            else:
                foundOther = True               
            
        ok_(foundModeling,'Modeling found')
        ok_(foundOther == False,'No other tasks where found')
        
        
        
        #query using STATUS
        tasks = user.getTasks(taskStatuses=[DONE_STATUS])
        
        foundStatus = False
        foundOther = False
        
        for t in tasks:
            if t.get('statusid') == DONE_STATUS:
                foundStatus = True
            else:
                foundOther = True               
            
        ok_(foundStatus,'status found')
        ok_(foundOther == False,'No other tasks where found')      
        
        #active project
        
        project = ftrack.getProject('bunny')
        task2 = project.createTask(taskName2,ftrack.TaskType(modeling),ftrack.TaskStatus(DONE_STATUS))
        task2.assignUser(user)
        
        allTasks = user.getTasks(activeProjectsOnly=False)
        activeTasks = user.getTasks(activeProjectsOnly=True)

        print "all:" + str(len(allTasks))
        print "active:" + str(len(activeTasks))
        ok_(len(allTasks) > len(activeTasks),"There are more tasks than active")
        
        
        
    def test_4_getusers(self):
        
        def createProject():
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
            taskName2 = str(uuid())
            showTask = show.createTask(taskName1,ftrack.TaskType(modeling),ftrack.TaskStatus(IN_PROGRESS_STATUS))
            seqTask = seq.createTask(taskName2,ftrack.TaskType(modeling),ftrack.TaskStatus(DONE_STATUS))           
            shotTask = shot.createTask(taskName2,ftrack.TaskType(modeling),ftrack.TaskStatus(DONE_STATUS))
            
            user = ftrack.getUser('standard')
            shotTask.assignUser(user)
            
            user = ftrack.getUser('jenkins')
            seqTask.assignUser(user)
            
            user = ftrack.getUser('root')
            showTask.assignUser(user)
            
            return show,seq,shot
        
        show,seq,shot = createProject()
        print shot.getUsers()
        ok_(len(shot.getUsers()) == 1, "1 user found")
        print seq.getUsers()
        ok_(len(seq.getUsers()) == 2, "2 user found")
        print show.getUsers()
        ok_(len(show.getUsers()) == 3, "3 user found")
        
        
        
    def test_5_attributes(self):
        
        user = ftrack.getUser('standard')
        
        thumbnailid = user.getThumbnail()
        
        ok_(thumbnailid == None,'could find thumbnailid')
        
        ok_(user.get('isactive'),'user is active')
        
        
        users = ftrack.getProject('test').getUsers()
        
        ok_(len(users) > 0,'users found')
        
        ok_(users[0].get('isactive'),'user is active')
        
        
        
    def test_6_getusers(self):
        
        users = ftrack.getUsers()
        
        found1 = False
        found2 = False
        
        for user in users:
            if user.getUsername() == 'bjorn.rydahl':
                found1 = True
                
            if user.getUsername() == 'jenkins':
                found2 = True
        
        ok_(found1 and found2, "Found users")
        

     
    
    @raises(ftrack.FTrackError)      
    def test_7_attribute(self):
        
        user = ftrack.getUser('standard')
        user.set('username',"hejhej")
        
          
    def test_8_customattribute(self):
        
        text = ftrack.getUUID()
        
        user = ftrack.getUser('standard')
        user.set('teststring',text)
        
        ok_(user.get('teststring') == text, 'text was set')

    def test_9_create_thumbnail(self):
        import os
        user = ftrack.User('jenkins')

        thumbnailpath = os.path.abspath("./data/thumbnail.jpg")
        thumb = user.createThumbnail(thumbnailpath)


