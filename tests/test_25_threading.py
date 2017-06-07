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
        
		import threading

		class SummingThread(threading.Thread):

		     def run(self):
		     	for i in range(1,10):
		        	ftrack.getProjects()


		thread1 = SummingThread()
		thread2 = SummingThread()
		thread1.start()
		thread2.start()
		thread1.join()
		thread2.join()

