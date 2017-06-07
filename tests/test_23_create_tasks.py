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


    def test_1_task_no_params(self):
        
        p = ftestutil.createProject()
        
        t = p.createTask('my task')

