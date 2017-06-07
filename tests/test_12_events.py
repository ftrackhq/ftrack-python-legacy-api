from nose.tools import *
import ftrack
from ftrack import asc, desc, limit, order_by, filter_by
from uuid import uuid1 as uuid
import sys
import datetime

class test_Types:


    def setUp(self):
        self.globalName = 'nose_test'

    def tearDown(self):
        pass


    def test_1_events(self):

        show = ftrack.getShowFromPath('test')

        date = datetime.datetime(1998, 2, 13, 9, 0)

        events = ftrack.getActivityEvents(
            projectId=show.getId(),
            fromEventId=0,
            fromDate=date,
            actions=['change.status.asset'],
            preloadObjects=True
        )
        success = False

        for e in events:
            if e.get('object'):
                success = True

        ok_(success,'contains data')


        version = events[0].getEntity()

        ok_(isinstance(version,ftrack.AssetVersion),'corrent entity')



        events = ftrack.getActivityEvents(projectId=show.getId(),fromEventId=0,fromDate=date,actions=['change.status.asset'],preloadObjects=False)
        success = False

        for e in events:
            if not e.get('object'):
                success = True

        ok_(success,'does not contain data')



        events = ftrack.getActivityEvents(fromEventId=1000,preloadObjects=False)
        success = False

        for e in events:
            if e.getId() < 1000:
                ok_(False,'bad fromEventId')
            else:
                success = True

        ok_(success,'fromEventId')



        events = ftrack.getActivityEvents(limit=2,preloadObjects=False)


        ok_(len(events) == 2,'limit is ok')

    def test_2_append_remove_from_list(self):
        # Get show and sequence, create new list on show and add two tasks to it, remove one task
        # Check for events

        show = ftrack.getShowFromPath('test')
        shot = ftrack.getShot('test.fog.s1')
        tasks = shot.getTasks()
        categories = ftrack.getListCategories()

        ok_(len(categories) > 0,"There are list categories")
        list = show.createList(ftrack.getUUID(),categories[0],ftrack.Task)
        list.append(tasks[0])
        list.append(tasks[1])

        list.remove(tasks[0])


        date = datetime.datetime(1998, 2, 13, 9, 0)
        append = ftrack.getActivityEvents(projectId=show.getId(),fromEventId=0,fromDate=date,actions=['append.to.list'],preloadObjects=True)
        remove = ftrack.getActivityEvents(projectId=show.getId(),fromEventId=0,fromDate=date,actions=['remove.from.list'],preloadObjects=True)


        ok_(len(append) >= 2,"Length of append events is correct")
        ok_(len(remove) >= 1,"Length of remove events is correct")
        
        
        
        
        