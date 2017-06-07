from nose.tools import ok_, assert_equal, raises
import ftrack
from ftrack import asc, desc, limit, order_by, filter_by
from uuid import uuid1 as uuid
import sys

from datetime import datetime, timedelta    

class test_Types:
    

    def setUp(self):
        self.globalName = 'nose_test'
    
    def tearDown(self):
        pass

    def test_1_create_phases(self):
        
        show = ftrack.getShow(['test'])

        startdate = datetime(2013, 7, 5, 12, 0, 0)

        phase = show.createPhase('description1', startdate, datetime.now() + timedelta(days=5))
        
        ok_(phase, 'Phase created correctly')
        
        assert_equal(phase.get('startdate'), startdate)

    def test_2_metadata(self):

        from uuid import uuid1

        theid = str(uuid1())

        show = ftrack.getShow(['test'])

        startdate = datetime(2013, 7, 5, 12, 0, 0)

        phase = show.createPhase('description1', startdate, datetime.now() + timedelta(days=5))
        phase.setMeta('someid', theid)

        foundId = False
        for phase in show.getPhases():
            if phase.getMeta('someid') == theid:
                foundId = True
                break

        ok_(foundId, 'Created phase found and metadata set ok')


    def test_3_assign_user(self):

        user = ftrack.getUsers()[0]

        show = ftrack.getShow(['test'])

        startdate = datetime(2013, 7, 5, 12, 0, 0)

        phase = show.createPhase('description1', startdate, datetime.now() + timedelta(days=5))
        phase.assignUser(user)

        users = phase.getUsers()

        ok_(len(users) == 1 and users[0].getId() == user.getId(), 'user is assigned ok')


    def test_4_unassign_user(self):

        allUsers = ftrack.getUsers()

        show = ftrack.getShow(['test'])

        startdate = datetime(2013, 7, 5, 12, 0, 0)

        phase = show.createPhase('description1', startdate, datetime.now() + timedelta(days=5))
        phase.assignUser(allUsers[0])
        phase.assignUser(allUsers[1])

        users = phase.getUsers()

        ok_(len(users) == 2, 'user is assigned ok')

        phase.unAssignUser(allUsers[0])

        users = phase.getUsers()

        ok_(len(users) == 1, 'user is unassigned ok')

    @raises(ftrack.FTrackError)
    def test_5_delete(self):

        show = ftrack.getShow(['test'])

        startdate = datetime(2013, 7, 5, 12, 0, 0)

        phase = show.createPhase('description1', startdate, datetime.now() + timedelta(days=5))

        beforeDelete = len(show.getPhases())

        phaseId = phase.getId()

        phase.delete()

        ok_(len(show.getPhases()) == beforeDelete-1, 'delete sucessful')

        # This should raise Exception
        ftrack.Phase(phaseId)



    @raises(ftrack.FTrackError)
    def test_6_date_is_none(self):

        show = ftrack.getShow(['test'])        
        show.createPhase('description1', datetime.now(), None)

    def testTaskTypes(self):
        '''Test adding and removing task types from phase.'''
        project = ftrack.getProject('test')
        phase = project.createPhase(
            'my description.',
            datetime.now(),
            datetime.now() + timedelta(days=5)
        )

        compositing = ftrack.TaskType('Compositing')
        animation = ftrack.TaskType('Animation')

        ok_(len(phase.getTaskTypes()) == 0, 'Phase has no task types.')

        phase.addTaskType(compositing)
        phase.addTaskType(animation)

        ok_(len(phase.getTaskTypes()) == 2, 'Phase should have 2 task types.')

        phase.removeTaskType(animation)

        ok_(len(phase.getTaskTypes()) == 1, 'Phase should have 1 task types.')

        assert_equal(
            compositing.getId(),
            phase.getTaskTypes()[0].getId(),
            'Should have the same ids.'
        )
