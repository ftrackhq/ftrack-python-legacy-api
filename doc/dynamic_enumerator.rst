..
    :copyright: Copyright (c) 2014 ftrack

.. _developing/legacy/dynamic_enumerator:

******************
Dynamic enumerator
******************

A dynamic enumerator is a custom attribute type that will fetch its values from
a remote service. Before the values are presented in a drop-down menu, they are
queried from the service. The query includes information about the current
context being edited which can be used to filter the values. The context
includes information about the current entity and unsaved changes if there are
any.

Example service
===============

This service handles two different enumerators, *product_category* and
*product_name*. *product_name* is filtered based on *product_category*. For
test purposes it will also output two test values for any other dynamic
enumerator.


.. literalinclude:: /resource/dynamic_enumerator.py
    :language: python
