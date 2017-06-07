# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import uuid
import datetime

import ftrack

from .tools import assert_equal


class TestTempData(object):
    '''Test TempData.'''

    def __init__(self, *args, **kw):
        '''Initialise test.'''
        super(TestTempData, self).__init__(*args, **kw)

    def testCreateTempData(self):
        '''Test creating temporary data.'''

        expiry = datetime.datetime.now() + datetime.timedelta(minutes=5)
        expiry = expiry.replace(microsecond=0)

        data = uuid.uuid1().hex

        tempDataWithExpiry = ftrack.createTempData(
            data, expiry=expiry
        )

        retrievedTempData = ftrack.TempData(id=tempDataWithExpiry.getId())

        assert_equal(
            retrievedTempData.get('data'), data, 'Temporary data is correct.'
        )

        assert_equal(
            retrievedTempData.get('expiry'), expiry,
            'Temporary expiry is correct.'
        )
