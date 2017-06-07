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


    def test_1_getchildren(self):
        
        
        shot = ftrack.Task("c410b0dc-6c58-11e1-8a63-f23c91df25eb")

        children = shot.getChildren()
        ok_(len(children) == 0, 'should be 0')


        seq = ftrack.Task("4f01f6b6-6c58-11e1-af10-f23c91df25eb")

        children = seq.getChildren()
        ok_(len(children) == 1, 'should be 1')
        ok_(children[0].getId() == "c410b0dc-6c58-11e1-8a63-f23c91df25eb", 'correct item')



        

        project = ftrack.Project("aa30f6c4-9811-11e1-95e3-f23c91df25eb")

        children = project.getChildren()
        ok_(len(children) == 4, 'should be 4')

        ids = []
        for item in children:
        	ids.append(item.getId())

        ok_('b5214a84-9811-11e1-b32d-f23c91df25eb' in ids, 'should be found')
        ok_('b749ba12-9811-11e1-857f-f23c91df25eb' in ids, 'should be found')
        ok_('b8658908-9811-11e1-9832-f23c91df25eb' in ids, 'should be found')




        	

        task = ftrack.Task("f8067608-9811-11e1-8cc1-f23c91df25eb")

        children = task.getChildren()
        ok_(len(children) == 0, 'should be 0')

    def test_3_episodes(self):

        p = ftestutil.createProject()

        e = p.createEpisode('episode')

        children = p.getChildren()
        ok_(len(children) == 1)
        ok_(children[0].getObjectType() == 'Episode' or children[1].getObjectType() == 'Episode','is episode')


        children = p.getChildren('Shot')
        ok_(len(children) == 0)


        children = p.getEpisodes()
        ok_(len(children) == 1)
        ok_(children[0].getObjectType() == 'Episode','is episode')

        p.createShot('my shot')

        children = p.getChildren('Shot')
        ok_(len(children) == 1)

        children = p.getShots()
        ok_(len(children) == 1)
        ok_(children[0].getObjectType() == 'Shot','is shot')



        seq = p.createSequence('my seq')

        children = p.getChildren('Sequence')
        ok_(len(children) == 1)

        children = p.getSequences()

        ok_(len(children) == 1)
        ok_(children[0].getObjectType() == 'Sequence','is seq')



        p.createAssetBuild('my asset build')

        children = p.getChildren('Asset Build')
        print children
        ok_(len(children) == 1)

        children = p.getAssetBuilds()
        ok_(len(children) == 1)
        ok_(children[0].getObjectType() == 'Asset Build','is asset build')


        seq.createShot('my shot')

        children = seq.getChildren('Shot')
        ok_(len(children) == 1)

        children = seq.getShots()
        ok_(len(children) == 1)
        ok_(children[0].getObjectType() == 'Shot','is shot')

    def test_5_create_seq_on_episode(self):

        p = ftestutil.createProject()

        ep = p.createEpisode('my edpisode')
        ep.createSequence('seq1')


        children = ep.getSequences()
        ok_(len(children) == 1)

