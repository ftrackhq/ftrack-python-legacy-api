# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os

import requests

from .tools import assert_equal, ok_, assert_raises

import ftrack

REVIEW_SESSION_ID = 'bbfeae42-5910-11e4-a871-3c0754282242'
READ_ONLY_API_KEY = '265ec93a-e43c-11e4-b74d-3c0754282242'
NO_ACCESS_API_KEY = '1edc65fa-e43c-11e4-a7c8-3c0754282242'


class test_Review:
    '''Test reviews.'''

    def testGetReviewSessionObjects(self):
        '''Test getting a review session.'''
        reviewSession = ftrack.ReviewSession(REVIEW_SESSION_ID)
        reviewSessionObjects = reviewSession.reviewSessionObjects()

        assert_equal(
            len(reviewSessionObjects), 1, 'All review session objects present.'
        )

    def testGetResolvedCloudUrl(self):
        '''Test getting a resolved cloud url.'''
        reviewSession = ftrack.ReviewSession(REVIEW_SESSION_ID)
        reviewSessionObject = reviewSession.reviewSessionObjects()[0]

        resolvedUrl = reviewSessionObject._resolveCloudUrl()
        response = requests.get(resolvedUrl)

        assert_equal(
            response.status_code, 200, 'Resolved url works as expected.'
        )

    def testAddRemoveReviewSessionObjects(self):
        '''Test add and remove review session objects from review session.'''

        # Get 'client review' test project.
        project = ftrack.Project('81b98c47-5910-11e4-901f-3c0754282242')

        # Get a reviewable AssetVersion from the 'client review' project.
        assetVersion = ftrack.AssetVersion(
            'a7519019-5910-11e4-804a-3c0754282242'
        )

        reviewSessionName = reviewSessionDescription = ftrack.getUUID()
        reviewSession = project.createReviewSession(
            reviewSessionName, reviewSessionDescription
        )

        ok_(reviewSession, 'Review session created successfully.')

        # Test to create and use syncing from AssetVersion.
        reviewSessionObject = reviewSession.createObject(
            assetVersion, syncAssetVersionData=True, name='Overridden name'
        )

        assert_equal(
            len(reviewSession.getObjects()), 1,
            'Correct number of review session objects on review session.'
        )

        assert_equal(
            ['010', 'previz', 'Version 1'],
            [
                reviewSessionObject.get('name'),
                reviewSessionObject.get('description'),
                reviewSessionObject.get('version')
            ],
            'Name, description and version has been synced correctly.'
        )

        reviewSessionObject.set('name', 'FOO')

        assert_equal(
            reviewSessionObject.get('name'), 'FOO',
            'Name updated correct.'
        )

        reviewSessionObject.delete()

        assert_equal(
            len(reviewSession.getObjects()), 0,
            'Correct number of review session objects on review session.'
        )

        # Test to create and use syncing from AssetVersion.
        reviewSessionObject = reviewSession.createObject(
            assetVersion, name='Custom name'
        )

        assert_equal(
            'Custom name', reviewSessionObject.get('name'),
            'Name has been set manually.'
        )

    def testCreateReviewSessionOnProject(self):
        '''Test create review session on project.'''

        # Get 'client review' test project.
        project = ftrack.Project('81b98c47-5910-11e4-901f-3c0754282242')

        reviewSessionCount = len(project.getReviewSessions())

        reviewSessionName = reviewSessionDescription = ftrack.getUUID()
        reviewSession = project.createReviewSession(
            reviewSessionName, reviewSessionDescription
        )

        ok_(reviewSession, 'Review session created successfully.')

        assert_equal(
            (reviewSessionCount + 1), len(project.getReviewSessions()),
            'Correct number of review sessions on project.'
        )

        reviewSession.set('name', 'FOO')
        assert_equal(
            reviewSession.get('name'), 'FOO',
            'Name updated correct.'
        )

    def testAddRemoveInviteeOnReviewSession(self):
        '''Test add and remove invitees from review session.'''

        # Get 'client review' test project.
        project = ftrack.Project('81b98c47-5910-11e4-901f-3c0754282242')

        reviewSessionName = reviewSessionDescription = ftrack.getUUID()
        reviewSession = project.createReviewSession(
            reviewSessionName, reviewSessionDescription
        )

        ok_(reviewSession, 'Review session created successfully.')

        assert_equal(
            len(reviewSession.getInvitees()), 0,
            'Correct number of invitees on review session'
        )

        invitee = reviewSession.createInvitee(
            email='john.doe@example.com', name='John Doe'
        )

        ok_(invitee, 'Invitee added correctly.')

        assert_equal(
            len(reviewSession.getInvitees()), 1,
            'Correct number of invitees on review session'
        )

        # Instantiate from id.
        invitee = ftrack.ReviewSessionInvitee(
            invitee.get('id')
        )

        invitee.set('name', 'FOO')

        assert_equal(
            invitee.get('name'), 'FOO',
            'Name updated correct.'
        )

        invitee.delete()

        assert_equal(
            len(reviewSession.getInvitees()), 0,
            'Correct number of invitees on review session'
        )

        with assert_raises(ftrack.FTrackError):
            invitee = reviewSession.createInvitee(
                email='invalid-email', name='John Doe'
            )

    def testGetSetStatusOnReviewSessionObject(self):
        '''Test get and set statuses for review session object.'''

        # Get 'client review' test project.
        project = ftrack.Project('81b98c47-5910-11e4-901f-3c0754282242')

        # Get a reviewable AssetVersion from the 'client review' project.
        assetVersion = ftrack.AssetVersion(
            'a7519019-5910-11e4-804a-3c0754282242'
        )

        reviewSessionName = reviewSessionDescription = ftrack.getUUID()
        reviewSession = project.createReviewSession(
            reviewSessionName, reviewSessionDescription
        )

        ok_(reviewSession, 'Review session created successfully.')

        # Test to create and use syncing from AssetVersion.
        reviewSessionObject = reviewSession.createObject(
            assetVersion, syncAssetVersionData=True, name='Overridden name'
        )

        invitee = reviewSession.createInvitee(
            email='john.doe@example.com', name='John Doe'
        )

        statuses = reviewSessionObject.getStatuses()

        assert_equal(len(statuses), 0, 'Correct number of statuses.')

        status = reviewSessionObject.setStatus('approved', invitee)
        statuses = reviewSessionObject.getStatuses()

        assert_equal(len(statuses), 1, 'Correct number of statuses.')
        assert_equal(status.get('status'), 'approved', 'Correct status.')
        assert_equal(
            statuses[0].get('status'),
            'approved',
            'Correct status {0} == {1}.'.format(
                statuses[0].get('status'), 'approved'
            )
        )

        with assert_raises(ftrack.FTrackError):
            reviewSessionObject.setStatus('invalid-status', invitee)

        class InvalidInvitee(object):
            '''Dummy Invitee class for testing.'''

            def getId(self):
                return 'invalid-id'

        with assert_raises(ftrack.FTrackError):
            reviewSessionObject.setStatus('approved', InvalidInvitee())

        status = reviewSessionObject.setStatus('require_changes', invitee)
        statuses = reviewSessionObject.getStatuses()

        assert_equal(len(statuses), 1, 'Correct number of statuses.')
        assert_equal(
            status.get('status'), 'require_changes', 'Correct status.'
        )

    def testPermissions(self):
        '''Test create, update, delete permissions.'''

        # Get 'client review' test project.
        project = ftrack.Project('81b98c47-5910-11e4-901f-3c0754282242')

        # Get a reviewable AssetVersion from the 'client review' project.
        assetVersion = ftrack.AssetVersion(
            'a7519019-5910-11e4-804a-3c0754282242'
        )

        reviewSessionName = reviewSessionDescription = ftrack.getUUID()
        reviewSession = project.createReviewSession(
            reviewSessionName, reviewSessionDescription
        )

        ok_(reviewSession, 'Review session created successfully.')

        # Test to create and use syncing from AssetVersion.
        reviewSessionObject = reviewSession.createObject(
            assetVersion, syncAssetVersionData=True, name='Overridden name'
        )

        invitee = reviewSession.createInvitee(
            email='john.doe@example.com', name='John Doe'
        )

        reviewSessionObject.setStatus('approved', invitee)

        _originalKey = os.environ['FTRACK_APIKEY']

        os.environ['FTRACK_APIKEY'] = READ_ONLY_API_KEY

        with assert_raises(ftrack.PermissionDeniedError):
            reviewSession.createInvitee(
                email='john.doe+1@example.com', name='John Doe'
            )

        with assert_raises(ftrack.PermissionDeniedError):
            reviewSessionObject.setStatus('require_changes', invitee)

        with assert_raises(ftrack.PermissionDeniedError):
            reviewSession.set('name', 'FOO')

        with assert_raises(ftrack.PermissionDeniedError):
            reviewSessionObject.set('name', 'FOO')

        with assert_raises(ftrack.FTrackError):
            invitee.delete()

        with assert_raises(ftrack.FTrackError):
            reviewSessionObject.delete()

        with assert_raises(ftrack.FTrackError):
            reviewSession.delete()

        os.environ['FTRACK_APIKEY'] = NO_ACCESS_API_KEY

        with assert_raises(ftrack.PermissionDeniedError):
            project.getReviewSessions()

        with assert_raises(ftrack.PermissionDeniedError):
            reviewSession.getObjects()

        os.environ['FTRACK_APIKEY'] = _originalKey

    def testCreateNotesOnReviewSessionObjects(self):
        '''Create notes on review session objects.'''
        project = ftrack.Project('81b98c47-5910-11e4-901f-3c0754282242')

        assetVersion = ftrack.AssetVersion(
            'a7519019-5910-11e4-804a-3c0754282242'
        )

        reviewSessionName = reviewSessionDescription = ftrack.getUUID()
        reviewSession = project.createReviewSession(
            reviewSessionName, reviewSessionDescription
        )

        reviewSessionObject = reviewSession.createObject(
            assetVersion, syncAssetVersionData=True, name='Overridden name'
        )

        noteText = ftrack.getUUID()
        note = reviewSessionObject.createNote(
            noteText
        )
        ok_(note.get('text') == noteText, 'Note text is the same.')
