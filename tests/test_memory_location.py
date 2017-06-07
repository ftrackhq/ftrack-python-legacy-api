# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack

import ftrack

from . import test_location


class TestMemoryLocation(test_location.BaseLocationTest):
    '''Test memory location implementation.'''

    def getLocation(self):
        '''Return location instance to test against.'''
        return ftrack.Location('location_c')
