..
    :copyright: Copyright (c) 2014 FTrack

***************
Resolver plugin
***************

A plugin that listens for location resolve events and attempts to use local
location plugins to determine the full filesystem paths to display in the web
interface.

A :ref:`standard resolver <using/locations/administration/resolver_service>`
plugin runs on the server for the builtin locations, but for custom locations
customise this plugin to also resolve their paths in the web interface.

.. literalinclude:: /resource/resolver.py
    :language: python

To use, download :download:`resolver.py </resource/resolver.py>` and place on
the :envvar:`FTRACK_EVENT_PLUGIN_PATH`. In addition, ensure that the relevant
local location plugins are also present on the
:envvar:`FTRACK_LOCATION_PLUGIN_PATH`. Then run a :ref:`event node
<developing/legacy/locations/example/event_node>`.