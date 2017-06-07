# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import uuid

import ftrack

from .tools import assert_equal, assert_raises


class TestServerAccessor(object):
    '''Test server accessor.'''

    def setUp(self):
        '''Perform per test setup.'''

    def tearDown(self):
        '''Perform per test teardown.'''

    def testReadAndWrite(self):
        '''Read and write data.'''
        randomData = uuid.uuid1().hex
        component = ftrack.createComponent(location=None)
        componentId = component.getId()

        accessor = ftrack.ServerAccessor()
        httpFile = accessor.open(componentId, mode='wb')
        httpFile.write(randomData)
        httpFile.close()

        data = accessor.open(componentId, 'r')
        assert_equal(data.read(), randomData)
        data.close()

    def testRemoveData(self):
        '''Remove data from accessor.'''
        randomData = uuid.uuid1().hex
        component = ftrack.createComponent(location=None)
        componentId = component.getId()

        accessor = ftrack.ServerAccessor()
        httpFile = accessor.open(componentId, mode='wb')
        httpFile.write(randomData)
        httpFile.close()

        accessor.remove(componentId)

        data = accessor.open(componentId, 'r')
        with assert_raises(ftrack.AccessorResourceNotFoundError):
            data.read()
