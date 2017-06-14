# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack

import os
import urlparse
import urllib2
import urllib

from nose.tools import ok_

import ftrack


class TestUserApiKeys(object):
    '''Class representing user api key tests.'''

    def test_1_task_no_params(self):
        '''Reset user api key.'''
        user = ftrack.getUser('jenkins')
        oldKey = user.getApiKey()
        user.resetApiKey()
        newKey = user.getApiKey()
        ok_(oldKey != newKey, 'Must be a new key')

    def testGetAttachment(self):
        '''Try to download a thumbnail using api keys without error.'''
        user = ftrack.getUser('jenkins')
        myShow = ftrack.getShowFromPath("test")

        myShow.createThumbnail(
            os.path.join(os.path.dirname(__file__), 'data/thumbnail.jpg')
        )
        url = myShow.getThumbnail()

        imgRequest = urllib2.Request(url)
        urllib2.urlopen(imgRequest).read()

        # Update url with new api key.
        params = {'apiKey': user.getApiKey()}
        url_parts = list(urlparse.urlparse(url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urllib.urlencode(query)
        url = urlparse.urlunparse(url_parts)

        imgRequest = urllib2.Request(url)
        urllib2.urlopen(imgRequest).read()
