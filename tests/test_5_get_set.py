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


    def test_1_project_path(self):
        
        show = ftrack.getShowFromPath('test')
        
        oldPlatform = sys.platform
        
        try:
            #windows
            sys.platform = "win64"
            path = show.getPath()
            ok_(path == "c:\\ftrack\\test\\test", "Windows path is incorrect.")
            path = show.getPath(full=True)
            ok_(path == "c:\\ftrack\\test\\test\\ftrack\\assets", "Windows path is incorrect")

            #linux
            sys.platform = "linux2"
            path = show.getPath()
            ok_(path == '/tmp/test', "Unix path is incorrect")
            path = show.getPath(True)
            ok_(path == '/tmp/test/ftrack/assets', "Unix path is incorrect")

        finally:
            sys.platform = oldPlatform
        
        
    def test_2_set_status(self):
        
        myShot = ftrack.getShot("test.python_api.shot1")
        
        asset = myShot.getAsset('custom',assetType='dai')
        version = asset.getVersions()[0]
        
        status = myShot.getSequence().getShow().getVersionStatuses()[0]
        
        version.setStatus(status)
        
        
        ok_(version.get('statusid') == status.get('statusid'),"Status was set")
        
        
    def test_3_meta(self):
        
        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        
        assets = myShot.getAssets()
        
        v = assets[0].getVersions()[0]
        
        from uuid import uuid1 as uuid
        
        text = str(uuid())
        
        v.setMeta('hej',text)
        
        result = v.getMeta('hej')
        
        ok_(result == text,"Meta is correct")
        
        
        allMeta = v.getMeta()
        
        ok_(allMeta['hej'] == text,"Meta is correct")
        
        
        #set several
        text1 = str(uuid())
        text2 = str(uuid())
        meta = {
            'hej' : text1,
            'hej2' : text2
        }
        v.setMeta(meta)
        
        allMeta = v.getMeta()
        ok_(allMeta['hej'] == text1,"Meta is correct")
        ok_(allMeta['hej2'] == text2,"Meta is correct")
        
        
        #NOTE
        note = myShot.createNote("hej hej")
        note.setMeta('hej',text)
        
        ok_(note.getMeta('hej') == text,"Meta is correct")
        
        #Shot
        myShot.setMeta('test',text)
        ok_(myShot.getMeta('test') == text,"Meta is correct")
        
        
    def test_4_dependencies(self):
        
        myShot = ftrack.getShot("test.python_api.shot2")
        tasks = myShot.getTasks()
        
        t1 = None
        t2 = None
        t3 = None
        
        for t in tasks:
            if t.getName() == 't1':
                t1 = t
            if t.getName() == 't2':
                t2 = t
            if t.getName() == 't3':
                t3 = t
        
        
        successors = t1.getSuccessors()
        ok_(len(successors) == 1,"has one successor")
        ok_(successors[0].getName() == 't2',"has one successor")
        ok_(successors[0]._type == 'task',"is task")
        
        successors = t2.getSuccessors()
        ok_(len(successors) == 1,"has one successor")
        ok_(successors[0].getName() == 't3',"has one successor")
        
        successors = t3.getSuccessors()
        ok_(len(successors) == 0,"has no successors")
        
        

        predecessors = t3.getPredecessors()
        ok_(len(predecessors) == 1,"has one predecessor")
        ok_(predecessors[0].getName() == 't2',"predecessor is t2")
        
        predecessors = t2.getPredecessors()
        ok_(len(predecessors) == 1,"has one predecessor")
        ok_(predecessors[0].getName() == 't1',"predecessor is t1")
        
        predecessors = t1.getPredecessors()
        ok_(len(predecessors) == 0,"has no predecessor")
        
        
    def test_5_set_shot_status(self):
        
        myShot = ftrack.getShot("test.python_api.shot1")
        statuses = myShot.getParents()[-1].getStatuses('Shot')
        status1 = statuses[0]
        status2 = statuses[1]
        
        myShot.setStatus(status1)
        
        ok_(myShot.getStatus().getId() == status1.getId(),"Status1 was set")
        
        myShot.setStatus(status2)
        
        ok_(myShot.getStatus().getId() == status2.getId(),"Status2 was set")
        ok_(myShot.getStatus().getId() != status1.getId(),"Status2 was set")
        
        
        
    def test_6_set(self):
        from random import randint
        
        #Shot
        myShot = ftrack.getShot("test.python_api.shot1")
        statuses = myShot.getParents()[-1].getStatuses('Shot')
        
        fstart = randint(100,1000)
        fend = fstart + 100
        
        myShot.set('fstart',fstart)
        myShot.set('fend',fend)
        
        myShot = ftrack.getShot("test.python_api.shot1")
        
        ok_(myShot.getFrameStart() == fstart,"fstart was set")
        ok_(myShot.getFrameEnd() == fend,"fend was set")
        
        
        
        fstart = str(randint(100,1000))
        fend = str(int(fstart) + 100)
        
        myShot.set('fstart',fstart)
        myShot.set('fend',fend)
        
        myShot = ftrack.getShot("test.python_api.shot1")
        
        ok_(myShot.getFrameStart() == int(fstart),"fstart was set")
        ok_(myShot.getFrameEnd() == int(fend),"fend was set")
        
        
    def test_7_getUserAndTasks(self):
        
        user = ftrack.User('jenkins')
        
        ok_(user.getUsername() == 'jenkins',"Username is correct")
        
        tasks = user.getTasks()
        
        ok_(len(tasks) > 0,"Username is correct")
        
        
    def test_8_getParent(self):
        myShot = ftrack.getShot("test.python_api.shot1")
        myTask = myShot.getTasks()[0]
        
        shot = myTask.getParent()
        ok_(shot.getName() == 'shot1',"Shot name is correct")
        
        seq = myShot.getParent()
        ok_(seq.getName() == 'python_api',"Sequence name is correct")
        
        show = seq.getParent()
        ok_(show.getName() == 'test',"Project name is correct")

        asset = myShot.getAsset('custom', 'Dailies')
        version = asset.getVersions()[0]
        component = version.getComponent()

        version = component.getParent()
        ok_(type(version).__name__ == 'AssetVersion',"Version is correct")
        
        asset = version.getParent()
        ok_(type(asset).__name__ == 'Asset',"Asset is correct")
        
    def test_9_getParents(self):
        myShot = ftrack.getShot("test.python_api.shot1")
        myTask = myShot.getTasks()[0]
        taskParents = myTask.getParents()
        
        ok_(taskParents[0].getName() == 'shot1',"Shot name is correct")
        ok_(taskParents[1].getName() == 'python_api',"Seq name is correct")
        ok_(taskParents[2].getName() == 'test',"Project name is correct")

        asset = myShot.getAsset('custom', 'Dailies')
        version = asset.getVersions()[0]
        component = version.getComponent()

        componentParents = component.getParents()
        
        ok_(type(componentParents[0]).__name__ == 'AssetVersion',
            'Version is not correct')
        ok_(type(componentParents[1]).__name__ == 'Asset',
            'Asset is not correct')
        ok_(type(componentParents[2]).__name__ == 'Task',
            'Shot is not correct')
        
    def test_10_assets(self):
        from random import randint
        
        #Shot
        myShot = ftrack.getShot("test.python_api.shot2")
        
        asset = myShot.createAsset('blaha','dai')
        
        newName = str(uuid())
        asset.set('name',newName)
        
        
        
        ok_(asset.get('name') == newName,"Asset name was updated")

        asset = ftrack.Asset(asset.getId())
        ok_(asset.get('name') == newName,"Asset name was updated2")
        
        
    def test_11_assign(self):
        
        #Shot
        myShot = ftrack.getShot("test.python_api.shot2")
        
        task = myShot.getTasks()[0]
        
        standard = ftrack.User('standard')
        
        task.assignUser(standard)
        
        t = task.getUsers()[0]
        ok_(t.getUsername() == 'standard','user is now assigned')
        
        task.unAssignUser(standard)

    def test_13_version(self):
        
        import datetime

        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        myTask = myShot.getTasks()[0]
        assetName = str(uuid())
        asset = myShot.createAsset(name=assetName,assetType='dai',task=myTask)
        version = asset.createVersion(taskid=myTask.getId())

        
        quicktimeComponent = version.createComponent()
    
        #Export
        asset.publish()        
        

        import datetime
        now = datetime.datetime.now().replace(microsecond=0)
        
                
        version.set('date',now)
        
        version = ftrack.AssetVersion(version.getId())
        
        ok_(version.get('date') == now)
        
        
        myTask.setEndDate(now)
        myTask.setStartDate(now)
        
        myTask = ftrack.Task(myTask.getId())
        
        ok_(myTask.getStartDate() == now)
               


    def test_14_getprojects(self):
        
        numProj = len(ftrack.getProjects())
        numProj2 = len(ftrack.getProjects(includeHidden=True))

        ok_(numProj < numProj2, "Must be more projects when hidden are included")


    def test_15_create_dependencies(self):

        """
        t1->t2,t3
        t4->t3
        """

        myShot = ftrack.getShotFromPath("test.python_api.shot1")

        shotTasks = ftestutil.createTasks(myShot,4)
        t1 = shotTasks[0]
        t2 = shotTasks[1]
        t3 = shotTasks[2]
        t4 = shotTasks[3]

        t1.addSuccessor(t2)

        s = t1.getSuccessors()
        ok_(len(s) == 1, 'must have one')
        ok_(s[0].getId() == t2.getId(), 'must be correct one')

        t1.addSuccessor(t3)

        s = t1.getSuccessors()
        ok_(len(s) == 2, 'must have two')


        s = t3.getPredecessors()
        ok_(len(s) == 1, 'must have one')

        t3.addPredecessor(t4)

        s = t4.getSuccessors()
        ok_(len(s) == 1, 'must have one')
        ok_(s[0].getId() == t3.getId(), 'must be correct one')


        s = t3.getPredecessors()
        ok_(len(s) == 2, 'must have two')


        #remove
        t3.removePredecessor(t4)
        s = t3.getPredecessors()
        ok_(len(s) == 1, 'must have one')
        ok_(s[0].getId() == t1.getId(), 'must be correct one')

        t1.removeSuccessor(t3)
        s = t1.getSuccessors()
        ok_(len(s) == 1, 'must have one')
        ok_(s[0].getId() == t2.getId(), 'must be correct one')

        for t in shotTasks:
            t.delete()

    @raises(ftrack.FTrackError)
    def test_16_create_dependencies_duplicate(self):

        myShot = ftrack.getShotFromPath("test.python_api.shot1")

        shotTasks = ftestutil.createTasks(myShot,2)
        t1 = shotTasks[0]
        t2 = shotTasks[1]

        try:
            t1.addSuccessor(t2)
            t1.addSuccessor(t2)
        finally:
            for t in shotTasks:
                t.delete()
