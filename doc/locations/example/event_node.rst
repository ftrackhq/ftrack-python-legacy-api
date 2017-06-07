..
    :copyright: Copyright (c) 2014 ftrack

.. _developing/legacy/locations/example/event_node:

********************
Event processor node
********************

The ftrack :ref:`API <developing/legacy/api_reference>` provides support for
subscribing to events for real time feedback and interaction within the ftrack
system. It can be useful to have one node running several subscribed handlers
for a variety of events.

.. literalinclude:: /resource/event_node.py
    :language: python

To use, download :download:`event_node.py </resource/event_node.py>`. Then
configure the environment (for example, setting the
:envvar:`FTRACK_EVENT_PLUGIN_PATH` and :envvar:`FTRACK_LOCATION_PLUGIN_PATH`
environment variables). Finally run the node with :term:`Python`::

    $ python event_node.py

To stop processing use :kbd:`Ctrl-C`.

