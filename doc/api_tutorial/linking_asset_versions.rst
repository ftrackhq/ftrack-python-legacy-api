..
    :copyright: Copyright (c) 2014 ftrack

.. py:currentmodule:: ftrack

.. _developing/legacy/api_tutorial/linking_asset_versions:

**********************
Linking asset versions
**********************

.. image:: /image/link_versions.jpg

:term:`Asset versions <asset version>` can be liked together to keep track of
which :term:`version <asset version>` was used in other
:term:`versions <asset version>` (a dependency). This is useful when making
changes to figure out what the change will affect and what has to be redone (for
example, a new render).

To link :term:`versions <asset version>` together use
:py:meth:`AssetVersion.addUsesVersions`.

First, create two new :term:`assets <asset>` (see
:ref:`developing/legacy/api_tutorial/publishing` for more details) and an
:term:`asset version` for each::

    shot = ftrack.getShot(['dev_tutorial', '001', '010'])

    geoAsset = shot.createAsset(name='warriorModel', assetType='geo')
    geoVersion = geoAsset.createVersion(comment='First pass.')
    geoAsset.publish()

    rigAsset = shot.createAsset(name='warriorRig', assetType='rig')
    rigVersion = rigAsset.createVersion(comment='First pass.')
    rigAsset.publish()

Now link the two together creating a dependency (the rig version used the geo
version)::

    rigVersion.addUsesVersions(versions=[geoVersion])

It is also possible to see all :term:`asset versions <asset version>` that are
used::

    print rigVersion.usesVersions()
    print geoVersion.usesVersions()

