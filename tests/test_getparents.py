# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack

import os
import glob

import clique

import ftestutil
from .tools import assert_equal


class TestGetParents():
    '''Test getParents.'''

    def __init__(self):
        '''Initialise test.'''
        self.dataPath = os.path.join(os.path.dirname(__file__), 'data')
        self.componentPath = os.path.join(
            self.dataPath, 'sequence', 'file.001.jpg'
        )

        collections, _ = clique.assemble(
            glob.glob(os.path.join(self.dataPath, 'sequence', '*.jpg'))
        )
        self.sequenceCollection = collections[0]
        self.sequenceComponentDescription = self.sequenceCollection.format()

    def setUp(self):
        '''Perform per test setup.'''
        self.project = ftestutil.createProject()
        self.sequence = self.project.createSequence('seq1')
        self.shot = self.sequence.createShot('010')
        self.task = ftestutil.createTasks(self.shot)
        self.asset = self.shot.createAsset('myasset', 'dai')
        self.version = self.asset.createVersion(taskid=self.task)
        self.fileComponent = self.version.createComponent(
            'file',
            path=self.componentPath
        )
        self.sequenceComponent = self.version.createComponent(
            'sequence',
            path=self.sequenceComponentDescription
        )

    def tearDown(self):
        '''Perform per test teardown.'''
        self.project.delete()

    def testGetParentsFromTask(self):
        '''Get parents from a task.'''
        parents = self.task.getParents()

        assert_equal(len(parents), 3, 'Length of parents is not correct.')
        assert_equal(
            parents[0].getName(),
            self.shot.getName(),
            'Shot name is not correct.'
        )
        assert_equal(
            parents[1].getName(),
            self.sequence.getName(),
            'Sequence name is not correct.'
        )
        assert_equal(
            parents[2].getName(),
            self.project.getName(),
            'Project name is not correct.'
        )

    def testGetParentsFromVersion(self):
        '''Get parents from version'''
        parents = self.version.getParents()

        assert_equal(len(parents), 4, 'Length of parents is not correct.')

        assert_equal(
            parents[0].getName(),
            self.asset.getName(),
            'Asset name is not correct.'
        )

    def testGetParentsFromFileComponent(self):
        '''Get parents from file component'''
        parents = self.fileComponent.getParents()

        assert_equal(len(parents), 5, 'Length of parents is not correct.')

    def testGetParentsFromSequenceComponent(self):
        '''Get parents from sequence component'''
        parents = self.sequenceComponent.getParents()

        assert_equal(len(parents), 5, 'Length of parents is not correct.')

    def testGetParentsFromSequenceFileComponent(self):
        '''Get parents from file component in sequence'''
        parents = self.sequenceComponent.getMembers()[0].getParents()

        assert_equal(len(parents), 6, 'Length of parents is not correct.')
