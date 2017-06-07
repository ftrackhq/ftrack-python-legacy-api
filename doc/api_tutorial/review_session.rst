..
    :copyright: Copyright (c) 2015 ftrack

.. _developing/legacy/api_tutorial/review_session:

************************
Managing review sessions
************************

Client review sessions can be created and listed from a project instance:
    
    .. code-block:: python

        # Create a new review session on a project
        project = ftrack.getProjects()[0]

        project.createReviewSession(
            name='Weekly review',
            description='See updates from last week.'
        )

        # List all review session on a project

        reviewSessions = project.getReviewSessions()

        for reviewSession in reviewSessions:
            print reviewSession.get('name')


To add objects to a review session use
:meth:`ftrack.ReviewSession.createObject` and specify a name
and referencing version.:

    .. code-block:: python

        # Get a review session and a reviewable asset version.
        reviewSession = # Get or create a review session from a project.
        assetVersion = # Get a reviewable asset version.

        # Setting `syncAssetVersionData` to True to copy information like
        # name from the version.
        reviewSession.createObject(
            assetVersion, syncAssetVersionData=True
        )

To list all objects in a review session use
:meth:`ftrack.ReviewSession.getObjects`.:

    .. code-block:: python

        reviewSession = # Get a review session from a project.
        reviewSessionObjects = reviewSession.getObjects()

        for reviewSessionObject in reviewSessionObjects:
            print reviewSessionObject.get('name')

As with objects you can add and list invitees to a review session using
:meth:`ftrack.ReviewSession.createInvitee` and
:meth:`ftrack.ReviewSession.getInvitees`.

To set the status of a object use :meth:`ftrack.ReviewSessionObject.setStatus`
together with an invitee instance.:

.. code-block:: python

        reviewSession = # Get a review session from a project.
        object = reviewSession.getObjects()[0]
        invitee = reviewSession.getInvitees()[0]

        object.setStatus('approved', invitee)
