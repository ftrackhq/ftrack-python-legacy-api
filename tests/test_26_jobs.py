# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack

import os

from nose.tools import *

import ftrack
import random

from .tools import assert_raises


class test_Jobs:

    def setUp(self):
        self.globalName = 'nose_test'

    def tearDown(self):
        pass

    def _set_and_check_status(self, job, status):
        job.setStatus(status)
        job = ftrack.Job(job.getId())
        ok_(job.get('status') == status, "Status is %s" % status)

    def _create_and_check_job(self):
        status = random.choice(["queued", "running", "done", "failed"])

        job = ftrack.createJob(description="My test job", status=status)
        ok_(job.get('status') == status, "Status is %s" % status)

        return job

    def test_1_create_job(self):
        # Create job with default user
        for i in range(15):
            job = self._create_and_check_job()

        self._set_and_check_status(job, 'running')
        self._set_and_check_status(job, 'done')
        self._set_and_check_status(job, 'failed')

    def test_2_set_all_failed(self):

        allJobs = ftrack.getJobs()
        countAll = len(allJobs)
        for job in allJobs:
            job.setStatus('running')

        allJobs = ftrack.getJobs(status='running')
        countFail = len(allJobs)

        for job in allJobs:
            job.setStatus('done')

        allJobs = ftrack.getJobs(status='done')
        countDone = len(allJobs)

        ok_(countAll == countDone == countFail, "All counts is equal")

    def test_3_remove_all(self):
        allJobs = ftrack.getJobs()
        for job in allJobs:
            job.delete()

        ok_(len(ftrack.getJobs()) == 0, "All jobs are deleted")

    def test_4_create_on_other_user(self):
        bear = ftrack.User('carl.claesson')
        job = ftrack.createJob(description="My test job", status='running', user=bear)

        ok_(job.get('userid') == bear.getId(), "The user is Bjorn")

    def test_5_attachments(self):
        FILE_NAME = 'TEST_FILE.txt'
        job = ftrack.createJob(description="My test job", status='running')

        tmpFile = os.tmpfile()
        tmpFile.write('TEST 123')
        tmpFile.seek(0)

        job.createAttachment(tmpFile, fileName=FILE_NAME)

        tmpFile.close()

        attachments = job.getAttachments()

        ok_(len(attachments) == 1, 'Number of attachments ok')

        attach = attachments.pop()

        job.setStatus('done')

        componentFilename = '{0}.{1}'.format(
            attach.get('name'), attach.get('filetype').lstrip('.')
        )
        ok_(componentFilename == FILE_NAME, 'File properly attached')

    def test_6_set_invalid_status(self):
        '''Fail to set invalid status.'''
        user = ftrack.User('jenkins')

        with assert_raises(ftrack.FTrackError):
            ftrack.createJob(
                description='My test job', status='invalid-running', user=user
            )
