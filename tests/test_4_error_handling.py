from nose.tools import *
import ftrack
from ftrack import asc, desc, limit, order_by, filter_by
from uuid import uuid1 as uuid

class test_Types:
    

    def setUp(self):
        self.globalName = 'nose_test'
    
    def tearDown(self):
        pass


    def test_1_getFromPath(self):
        
        #Show
        show = ftrack.getShowFromPath('test')
        ok_(show.get('name') == 'test',"Name is correct")
        ok_(show._type == 'show',"Type is Show")
        
        show = ftrack.getShow(['test'])
        ok_(show.get('name') == 'test',"Name is correct")
        ok_(show._type == 'show',"Type is Show")
        
        #Sequence
        seq = ftrack.getSequenceFromPath('test.python_api')
        ok_(seq.get('name') == 'python_api',"Name is correct")
        ok_(type(seq).__name__ == 'Task',"Type is Sequence")
        
        seq = ftrack.getSequence(['test','python_api'])
        ok_(seq.get('name') == 'python_api',"Name is correct")
        ok_(type(seq).__name__ == 'Task',"Type is Sequence")        
        
        #Shot
        shot = ftrack.getShotFromPath('test.python_api.shot1')
        ok_(shot.get('name') == 'shot1',"Name is correct")
        ok_(type(shot).__name__ == 'Task',"Type is Shot") 
        
        shot = ftrack.getShot(['test','python_api','shot1'])
        ok_(shot.get('name') == 'shot1',"Name is correct")
        ok_(type(shot).__name__ == 'Task',"Type is Shot")         
        
        
        
        
#    @raises(ftrack.FTrackError)
#    def test_2_getShowFromPath(self):
#        entity = ftrack.getShowFromPath('test.python_api.shot1')
#        
#    @raises(ftrack.FTrackError)
#    def test_3_getSequenceFromPath(self):
#        entity = ftrack.getShotFromPath('test.python_api')
#        
#    @raises(ftrack.FTrackError)
#    def test_4_getShotFromPath(self):
#        entity = ftrack.getSequenceFromPath('test')
      
    @raises(ftrack.FTrackError)
    def test_5_get(self):
        show = ftrack.getShowFromPath('test')
        show.get('randomstuff')

    @raises(ftrack.FTrackError)
    def test_6_get(self):
        show = ftrack.getShowFromPath('test')
        show.set('randomstuff','hej')
        
    @raises(ftrack.FTrackError)
    def test_7_filter_by(self):
        
        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        asset = myShot.getAsset('custom',assetType='dai')
        
        versions = asset.getVersions(filter_by(username2='bjry2'),order_by(asc('ilp_version'),desc('ilp_increment')),limit(10))
                
    @raises(ftrack.FTrackError)
    def test_8_order_by(self):
        
        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        asset = myShot.getAsset('custom',assetType='dai')
        
        versions = asset.getVersions(filter_by(username='bjry'),order_by(asc('ilp_version3'),desc('ilp_increment')),limit(10))
                

        
        
        
#    @raises(ftrack.FTrackError)
#    def test_9_publish(self):
#        
#        myShot = ftrack.getShotFromPath("test.python_api.shot1")
#        myTask = myShot.getTasks()[0]
#        
#        asset = myShot.createAsset(name='my_first_asset',assetType='dai')
#        version = asset.createVersion(taskid=myTask.getId())
#        
#        version.getComponents()

        

    @raises(ftrack.FTrackError)
    def test_10_getShowFromPath(self):
        entity = ftrack.getShowFromPath(['test.python_api.shot1'])
        
        
        
        
        
        
        
    @raises(ftrack.FTrackError)
    def test_10_publish_taskastaskid(self):
        myShot = ftrack.getShotFromPath("test.python_api.shot1")
        myTask = myShot.getTasks()[0]
        
        asset = myShot.createAsset(name='my_first_asset',assetType='dai')
        version = asset.createVersion(taskid=str(myTask))

        quicktimeComponent = version.createComponent()
    
        #Export
        asset.publish()

        
    @raises(ftrack.FTrackError)
    def test_11_create_duplicate_show(self):
        #create show
        showfullname = ftrack.getUUID()
        showname = 'test'
        workflows = ftrack.getProjectSchemes()
        show = ftrack.createShow(showfullname,showname,workflows[0])
        
    @raises(ftrack.FTrackError)
    def test_12_create_duplicate_seq(self):
        #create sequence
        seqname = 'python_api'
        show = ftrack.getShowFromPath("test")
        seq = show.createSequence(seqname)
        
    @raises(ftrack.FTrackError)
    def test_13_create_duplicate_shot(self):
        #create shot
        shotname = 'shot1'
        seq = ftrack.getSequenceFromPath("test.python_api")
        shot = seq.createShot(shotname)
        
        
        
#    @raises(ftrack.FTrackError)
#    def test_14_set_status(self):
#        
#        myShot = ftrack.getShot("test.python_api.shot1")
#        task = myShot.getTasks()[0]
#        
#        taskStatus = ftrack.getTaskStatuses()[0]
#        
#        task.setStatus(taskStatus)
        
    @raises(ftrack.FTrackError)    
    def test_14_getObjects(self):
        
        #Shot
        myShot = ftrack.getShot(34)
        
        
        
    @raises(ftrack.FTrackError)    
    def test_15_setDuplicate(self):
        
        myShot = ftrack.getShotFromPath("test.python_api.shot1")

        assetName = str(uuid())
        asset = myShot.createAsset(name=assetName,assetType='dai')
        version1 = asset.createVersion()
        version2 = asset.createVersion()

        version2.set('version',1)

        asset.delete()

    def test_16_diagnostics(self):
        '''Test if supervisord is running.'''
        data = ftrack.getDiagnostics()
        ok_(data['running'], 'must be running')
