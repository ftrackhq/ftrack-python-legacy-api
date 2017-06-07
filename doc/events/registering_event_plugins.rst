..
    :copyright: Copyright (c) 2015 ftrack

.. _developing/legacy/events/registering_event_plugins:

*************************
Registering event plugins
*************************

Event plugins are used by the API to extend it with new functionality, e.g. 
event processing of ftrack update events or User invoked
:term:`actions <action>`.

When the API is instantiated, directories in the environment variable 
`FTRACK_EVENT_PLUGIN_PATH` will be searched for
:term:`event plugins <event plugin>`, python files which expose a `register`
function. These functions will be evaluated and can be used extend the API with
new functionality.

Configuring plugins via registry
================================

Quick setup
-----------

1. Create a directory where plugins will be stored. Place any plugins you want
loaded automatically when using the API there.

.. image:: /image/configuring_plugins_directory.png

2. Configure the `FTRACK_EVENT_PLUGIN_PATH` to point to the directory.

Validate arguments in plugin register function
----------------------------------------------

To make event and location plugin register functions work with both old and new
API the function should be updated to validate the input arguments.

.. code-block:: python
    
    import ftrack


    class Action(ftrack.Action):
        '''My Action class.'''


    def register(registry, **kw):
      '''Register action.'''

      logger = logging.getLogger(
          'ftrack_plugin:action.register'
      )

      # Validate that registry is the event handler registry. If not,
      # assume that register is being called to regiter Locations or from a new
      # or incompatible API, and return without doing anything.
      if registry is not ftrack.EVENT_HANDLERS:
          logger.debug(
              'Not subscribing plugin as passed argument {0!r} is not an '
              'ftrack.Registry instance.'.format(registry)
          )
          return

      ...

A similar check should be implemented when registering locations using
`FTRACK_LOCATION_PLUGIN_PATH`.

.. code-block:: python

    if registry is not ftrack.LOCATION_PLUGINS:
        ...
        return

.. seealso::

    To configure location plugins you will need to set the
    `FTRACK_LOCATION_PLUGIN_PATH`, see
    :ref:`using/locations/administration/configure` for more information.

.. note::

    The new
    `ftrack Python API <http://ftrack-python-api.rtd.ftrack.com/en/latest/>`_
    uses the `FTRACK_EVENT_PLUGIN_PATH` similar to the Legacy API with the
    addition that it also discovers Locations on the same path.
