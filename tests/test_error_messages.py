# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os

import ftrack
from .tools import assert_raises_regexp


BAD_USERNAME = 'bad_username'


class TestInvalidUsername():
    '''Test invalid username.'''

    def setUp(self):
        '''Setup test with bad LOGNAME.'''
        self.oldUsername = os.environ['LOGNAME']
        os.environ['LOGNAME'] = BAD_USERNAME

    def tearDown(self):
        '''Teardown test and set old LOGNAME.'''
        os.environ['LOGNAME'] = self.oldUsername

    def testInvalidUsername(self):
        '''Test using api with bad username and validate error message.'''
        testRegexp = 'Unvalid or inactive username.+{username}'.format(
            username=BAD_USERNAME
        )
        with assert_raises_regexp(ftrack.FTrackError, testRegexp):
            ftrack.getProjects()


class TestInvalidApiKey():
    '''Test invalid API key.'''

    def setUp(self):
        '''Setup test with bad FTRACK_APIKEY.'''
        self.oldApiKey = os.environ['FTRACK_APIKEY']
        os.environ['FTRACK_APIKEY'] = 'bad_api_key'

    def tearDown(self):
        '''Teardown test and set old FTRACK_APIKEY.'''
        os.environ['FTRACK_APIKEY'] = self.oldApiKey

    def testInvalidApiKey(self):
        '''Test using api with bad api key and validate error message.'''
        with assert_raises_regexp(ftrack.FTrackError, 'Api key is not valid'):
            ftrack.getProjects()
