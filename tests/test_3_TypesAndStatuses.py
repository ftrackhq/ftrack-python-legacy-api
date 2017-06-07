from nose.tools import *
import ftrack
from ftrack import asc, desc, limit, order_by, filter_by
from uuid import uuid1 as uuid
import ftestutil


class test_Types:
    

    def setUp(self):
        self.globalName = 'nose_test'
    
    def tearDown(self):
        pass


    def test_1_can_fetch_data(self):
        
        #shows
        ok_(len(ftrack.getShows()) > 0,"There are shows in FTrack")
        
        #types
        ok_(len(ftrack.getAssetTypes()) > 0,"There are getAssetTypes in FTrack")
        
        #types
        ok_(len(ftrack.getTaskTypes()) > 0,"There are getTaskTypes in FTrack")        
        
        #types
        ok_(len(ftrack.getTaskStatuses()) > 0,"There are getTaskStatuses in FTrack")

        # Get shot statuses.
        statuses = ftrack.getProject('test').getStatuses('Shot')
        ok_(len(statuses) > 0, 'There are getShotStatuses in FTrack')

        found = False
        for s in statuses:
            if s.getName() == 'Normal':
                found = True
        
        ok_(found,"Shot status is Normal")
        
        #types
        ok_(len(ftrack.getNoteCategories()) > 0,"There are getNoteCategories in FTrack")      
    
    def test_2_get_types_from_show(self):
        
        show = ftrack.getShows()[0]
        
        #types
        ok_(len(show.getTaskTypes()) > 0,"There are getTaskTypes in FTrack")
        
        #types
        ok_(len(show.getTaskStatuses()) > 0,"There are getTaskStatuses in FTrack")
        myType = show.getTaskTypes()[0]
        ok_(len(show.getTaskStatuses(myType.getId())) > 0,"There are getTaskStatuses in FTrack")
        
        #types
        ok_(len(show.getVersionStatuses()) > 0,"There are getVersionStatuses in FTrack")
        
        
      
    def test_3_asset_types(self):
        name = str(uuid())[:10]
        short = str(uuid())[:10]

        ftrack.createAssetType(name,short)

        found = False
        for t in ftrack.getAssetTypes():
            if t.get('short') == short and name == t.get('name'):
                found = True

        ok_(found,'created asset type')

    @raises(ftrack.FTrackError)
    def test_4_asset_types(self):
        name = str(uuid())[:10]
        short = str(uuid())[:10]

        ftrack.createAssetType(name,short)
        ftrack.createAssetType(name,short)

    def test_get_none_status(self):
        '''Get the status from an entity without a status set.'''
        project = ftestutil.createProject()
        sequence = project.createSequence('sequence')
        result = sequence.getStatus()
        assert_equal(result, None, 'Status was returned as None.')

    def test_get_none_type(self):
        '''Get the type from an entity without a type set.'''
        project = ftestutil.createProject()
        sequence = project.createSequence('sequence')
        result = sequence.getType()
        assert_equal(result, None, 'Type was returned as None.')
