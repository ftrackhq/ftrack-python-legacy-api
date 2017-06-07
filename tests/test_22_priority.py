from nose.tools import *
import ftrack
from ftrack import asc, desc, limit, order_by, filter_by
from uuid import uuid1 as uuid
import sys
import ftestutil

class test_priority:
    

    def setUp(self):
        self.globalName = 'nose_test'
    
    def tearDown(self):
        pass


    def test_1_getwidgeturl(self):
        
        p = ftestutil.createProject()
        t = ftestutil.createTasks(p)

        prio = t.getPriority()

        ok_(type(prio.getValue()) == type(0.0))


        blocker = ftrack.Priority('Blocker')

        t.setPriority(blocker)

        ok_(t.getPriority().getId() != prio.getId())

    def test_2_getprio(self):

        prios = ftrack.getPriorities()

        ok_(len(prios) > 0)