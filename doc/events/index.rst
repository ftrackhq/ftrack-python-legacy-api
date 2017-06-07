..
    :copyright: Copyright (c) 2014 ftrack

.. _developing/legacy/events:

******
Events
******

Events are generated in ftrack when things happen such as a task being updated
or a new version being published. Clients can listen to these events and perform
an action as a result. The action could be updating another related entity based
on a status change or generating folders when a new shot is created for example.

.. toctree::

    overview
    registering_event_plugins
