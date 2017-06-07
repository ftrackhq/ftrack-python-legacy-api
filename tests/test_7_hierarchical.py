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


       
    def test_1_h(self):
        
        #create show
        showfullname = ftrack.getUUID()
        showname = ftrack.getUUID()
        workflows = ftrack.getProjectSchemes()
        show = ftrack.createShow(showfullname,showname,workflows[0])
        
        
        #create sequence
        seqname = ftrack.getUUID()
        seq = show.createSequence(seqname)
        
        
        #create shot
        shotname = ftrack.getUUID()
        shot = seq.createShot(shotname)
        
        
        
        
        htest = shot.get('htest')
        ok_(htest == 0, 'htest on shot is 0')
        
        
        
        htest = seq.get('htest')
        ok_(htest == 0, 'htest seq is 0')
        
        seq.set('htest',3)
        
        htest = seq.get('htest')
        ok_(htest == 3, 'htest seq is 3')
        
        
        
        htest = ftrack.Shot(shot.getId()).get('htest')
        ok_(htest == 3, 'htest on shot is 3')
        
        
        
        show.set('htest',5)
        
        
        htest = ftrack.Shot(shot.getId()).get('htest')
        ok_(htest == 3, 'htest on shot is 3')
        
        
        htest = ftrack.Sequence(seq.getId()).get('htest')
        ok_(htest == 3, 'htest seq is 3')
        
        htest = ftrack.Show(show.getId()).get('htest')
        ok_(htest == 5, 'htest seq is 5')
        
        
        
        
        
        
        