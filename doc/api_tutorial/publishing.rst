..
    :copyright: Copyright (c) 2014 ftrack

.. _developing/legacy/api_tutorial/publishing:

**********
Publishing
**********

.. image:: /image/asset_model.jpg

To publish an :term:`asset`, you create a new :term:`asset version` containing
:term:`components <component>`.

First, create a new :term:`asset` under a shot (or query an existing one)::

    # Query a shot and a task to create the asset against.
    shot = ftrack.getShot(['dev_tutorial', '001', '010'])
    task = shot.getTasks()[0]

    # Create new asset.
    asset = shot.createAsset(name='forest', assetType='geo')

Next create a :term:`version <asset version>` on the :term:`asset`. Note that
you can also link the :term:`version <asset version>` to a particular task::

    # Create a new version for the asset.
    version = asset.createVersion(
        comment='Added more leaves.',
        taskid=task.getId()
    )

    # Get the calculated version number.
    print version.getVersion()

Then add the :term:`components <component>` that make up the
:term:`version <asset version>`::

    # Add some components.
    previewPath = '/path/to/forest_preview.mov'
    previewComponent = version.createComponent(path=previewPath)

    modelPath = '/path/to/forest_mode.ma'
    modelComponent = version.createComponent(name='model', path=modelPath)

And set the publish flag on the :term:`asset` so that its
:term:`versions <asset version>` appear in the web interface::

    # Publish.
    asset.publish()

It is also possible to set a thumbnail on the :term:`version <asset version>`::

    # Add thumbnail to version.
    thumbnail = version.createThumbnail('/path/to/forest_thumbnail.jpg')

And reuse that thumbnail elsewhere as well::

    # Set thumbnail on other objects without duplicating it.
    task.setThumbnail(thumbnail)

