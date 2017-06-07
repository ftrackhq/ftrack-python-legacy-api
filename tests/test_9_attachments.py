# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os
import urllib2
import tempfile
import filecmp

from nose.tools import ok_
import ftrack


class TestAttachment(object):
    '''Test attachment functionality.'''

    def testUploadAndDownloadAttachment(self):
        '''Upload attachment and download using the url.'''

        # Create a random file and upload as an attachment.
        randomFile = tempfile.NamedTemporaryFile(suffix='.jpeg')
        randomFile.write(os.urandom(1024))
        project = ftrack.getProject('test')
        component = project.createThumbnail(randomFile.name)

        # Download as another file.
        downloadedFile = tempfile.NamedTemporaryFile()
        urlSocket = urllib2.urlopen(component.getUrl())
        downloadedFile.write(urlSocket.read())

        # Compare files on disk to make sure they are the same.
        ok_(
            filecmp.cmp(randomFile.name, downloadedFile.name),
            'File is not the same.'
        )

        # Close the files to make sure they are deleted.
        randomFile.close()
        downloadedFile.close()
