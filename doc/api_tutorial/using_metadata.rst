..
    :copyright: Copyright (c) 2014 ftrack

.. py:currentmodule:: ftrack

.. _developing/legacy/api_tutorial/using_metadata:

**************
Using metadata
**************

Custom attributes are useful when there is a need to filter and sort the data in
the ftrack web interface. However, there is often data that is only useful for
scripts and is not necessary to clutter the web interface with. For this it can
be good to store *metadata* on the object. Metadata is saved as strings that
can be up to 64kb long. For example, it is possible to save :term:`JSON`
encoded data.

Any :py:class:`Metable` object can set and retrieve metadata using
:py:meth:`~Metable.setMeta` and :py:meth:`~Metable.getMeta` respectively::

    shot = ftrack.getShot(['dev_tutorial', '001', '010'])

    # Set metadata on the shot.
    shot.setMeta('extradata', 'my metadata')

    # Get the metadata from the shot.
    print shot.getMeta('extradata')

It is also possible to set multiple key, value pairs in one call::

    metadata = {
        'data1' : 'some data...',
        'data2' : 'some data2...',
        'data3' : 'some data3...',
    }

    # Set metadata on the shot.
    shot.setMeta(metadata)

    # Get part of the metadata from the shot.
    print shot.getMeta('data1')

    # Or all at the same time.
    storedMetadata = shot.getMeta()

    for key, value in storedMetadata.items():
        print '{0} = {1}'.format(key, value)

At present, any additional encoding and decoding must be performed separately.
For example, to store and retrieve :term:`JSON` encoded data::

    import json

    metadata = {
        'data1' : 'some data...',
        'data2' : 34,
        'data3' : 'some data3...'
    }

    # Set manually encoded metadata.
    shot.setMeta('jsonMetadata', json.dumps(metadata))

    # Get the encoded data.
    encodedMetadata = shot.getMeta('jsonMetadata')

    # Manually decode it.
    decodedMetadata = json.loads(encodedMetadata)

    for key, value in decodedMetadata.items():
        print '{0} = {1}'.format(key, value)

