# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import ftrack
from .tools import assert_equal


class TestDisks():
    '''Test Disks.'''

    def testGetDiskUsingConstructor(self):
        '''Fetch a disk using its id or name.'''
        disks = ftrack.getDisks()

        disk = ftrack.Disk(disks[0].getId())
        assert_equal(
            disk.getId(),
            disks[0].getId(),
            'This is not the same disk.'
        )

        disk = ftrack.Disk(disks[0].getName())
        assert_equal(
            disk.getId(),
            disks[0].getId(),
            'This is not the same disk.'
        )
