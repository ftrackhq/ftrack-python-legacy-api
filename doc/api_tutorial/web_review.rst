..
    :copyright: Copyright (c) 2016 ftrack

.. _developing/legacy/api_tutorial/web_review:

*************************
Publishing for web review
*************************

To create components using the ftrack legacy python API you can use the
helper method :meth:`ftrack.Review.makeReviewable`:

.. code-block:: python

    filepath = '/path/to/local/file.mov'

    # Create/query an asset
    asset = shot.createAsset(name='forest', assetType='geo')

    # Create a new version
    version = asset.createVersion(
        comment='Web reviewable version', taskid=task.getId()
    )

    # Use utility method to upload file, transcode it to appropriate formats
    # and create new components.
    ftrack.Review.makeReviewable(version, filepath=filepath)

    # Publish the version to make it visible in ftrack.
    version.publish()

.. note::

    The encoding of the files will occur asynchronous and the components
    might not be available when :meth:`ftrack.Review.makeReviewable` is done.

If you already have a file encoded in the correct format and want to bypass
the built-in encoding in ftrack, you can create the component manually
and add it to the `ftrack.server` location.

.. code-block:: python

    version = # Retrieve or create a version you want to use

    filepath = '/path/to/local/file.mp4'

    component = version.createComponent(
        'ftrackreview-mp4', path=filepath,
        location=ftrack.Location('ftrack.server')
    )

    # Meta data needs to contain *frameIn*, *frameOut* and *frameRate*.
    meta_data = json.dumps({
        'frameIn': 0,
        'frameOut': 150,
        'frameRate': 25
    })

    component.setMeta(key='ftr_meta', value=meta_data)

This will transfer the file to the `ftrack.server` location and enable it
for review in ftrack.

.. note::

    Make sure to use the pre-defined component names `ftrackreview-mp4`,
    `ftrackreview-webm` and `ftrackreview-image`. They are used to identify
    playable components in ftrack. You also need to set the `ftr_meta` on the
    components.

To publish an image for review the steps are similar:

.. code-block:: python

    version = # Retrieve or create a version you want to use

    filepath = '/path/to/image.jpg'

    component = version.createComponent(
        'ftrackreview-image', path=filepath,
        location=ftrack.Location('ftrack.server')
    )

    # Meta data needs to contain *format*.
    meta_data = json.dumps({
        'format': 'image'
    })

    component.setMeta(key='ftr_meta', value=meta_data)
