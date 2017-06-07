..
    :copyright: Copyright (c) 2014 FTrack

.. py:currentmodule:: ftrack

****************
Structure plugin
****************

The structure plugin is used to compute the initial :term:`resource identifier` 
for an entity in ftrack. A custom structure plugin needs to implement 
:py:func:`Structure.getResourceIdentifier` which accepts an entity as input.

When the structure plugin is used for a location the entity will be a
:term:`component`.

The structure plugin can also be used separately to generate folder structures 
based on actions or events.

.. literalinclude:: /resource/dumping_ground_structure.py
    :language: python

To use, download
:download:`dumping_ground_structure.py </resource/dumping_ground_structure.py>`
and place on the :envvar:`PYTHONPATH`. Then
:ref:`configure <using/locations/administration/configure>` a location to use it
as its structure.

.. warning::

    It is not recommended to use this structure in production and is provided
    purely for illustrative purposes.
