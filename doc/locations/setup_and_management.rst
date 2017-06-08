..
    :copyright: Copyright (c) 2014 ftrack

.. _using/locations/administration:

******************
Setup & management
******************

The locations API is built with flexibility in mind and makes use of
:term:`Python` plugins to allow a good level of customisation.

This guide will cover how to configure and register a plugin, setup the
environment to discover plugins and also look at how to manage locations through
the web interface.

.. note::

    The standard builtin locations require no further setup or configuration
    and it is not necessary to read the rest of this section to use them.

Before continuing, make sure that you are familiar with the general concepts
of locations by reading :ref:`using/locations`.

.. _using/locations/administration/configure:

Configuring location plugins
============================

To setup a new location you will need to configure a location plugin. As an
example, you can download :download:`data_storage_location.py
</resource/data_storage_location.py>` which has the following contents:

.. literalinclude:: /resource/data_storage_location.py

Each plugin should declare a *register* function at the module level that
accepts the *registry* to add the plugin to. This *register* function will be
called by the ftrack :ref:`API <developing/api_reference>` when location plugins
are being discovered.

The name of the location can be anything, but should **not** start with
``ftrack.``, since those are reserved for internal use.

A good rule of thumb is to try and group locations in a logical way. For
example, ``company.city.server`` or ``joes-laptop``.

The location can also be customized with an :term:`accessor` or structure of
choice. There are a few builtin ones to choose from or to develop custom ones
see the :ref:`development guide <developing/locations>`.

Setting up the environment
==========================

With the :term:`Python` module containing the new location in place it is time
to ensure that it can be discovered by the ftrack
:ref:`API <developing/api_reference>`.

Plugins are discovered automatically by searching in directories added to the
environment variable :envvar:`FTRACK_LOCATION_PLUGIN_PATH`.

.. warning::

    All :term:`Python` modules on the search path are imported so it is a good
    idea to store these plugins away from the standard :envvar:`PYTHONPATH`.

Example of how to set the environment variable in 
:abbr:`POSIX (Portable Operating System Interface)`:

.. code-block:: bash

    export FTRACK_LOCATION_PLUGIN_PATH=/path/to/plugins:/another/path/to/plugins

Example of how to set the environment variable in Windows:

.. code-block:: bash

    set FTRACK_LOCATION_PLUGIN_PATH=/path/to/plugins;/another/path/to/plugins

Folders are separated by the :abbr:`OS (Operating System)` specific path 
separator:

* ``:`` on :abbr:`POSIX (Portable Operating System Interface)`-compliant
  systems, such as Linux or Mac OS X
* ``;`` on Windows

Discovering location plugins
============================

With the environment configured correctly it is now possible to discover and
load the configured plugins within a :term:`Python` session using
:py:func:`ftrack.setup`:

.. code-block:: python

    import ftrack
    ftrack.setup()

Alternatively, call :py:func:`ftrack.LOCATION_PLUGINS.discover` manually:

.. code-block:: python

    import ftrack
    ftrack.LOCATION_PLUGINS.discover()

In both cases the plugins will be found and automatically bind to any future
:py:class:`~ftrack.Location` instance in the session:

.. code-block:: python

    >>> location = ftrack.Location('custom.location')
    >>> print location.getStructure()
    <FTrackCore.api.structure.id.IdStructure object at 0x0000000013178C50>

Manage locations from Web UI
============================

The primary place to manage locations is through the ftrack
:ref:`API <developing/api_reference>`, but it is also possible to add, rename
and delete a location (excluding the actual plugin) through the Web UI.

To access the locations settings in the web interface:

1. Open ftrack in your favorite browser (Chrome, Firefox or Safari)
2. Go to :menuselection:`System settings --> Advanced --> Locations`

This view provides a table of existing location names along with the total space
consumed by all components in each location. Use the icons to rename or delete
any of the locations, and the button above the table to create new ones.

.. figure:: /image/settings_advanced_locations_page.jpg

    Screenshot of the locations settings view in the web interface.

.. _using/locations/administration/resolver_service:

Built in resolver service
=========================

The ftrack server has a built in resolver service. The resolver is used to
generate the full path of a component for a specified location. The built in
resolver is only be able to resolve components for any of the built in
locations. For other locations a custom 
:doc:`Resolver plugin </locations/example/resolver_plugin>`
must be setup.

It is common that only a part of the filepath is stored in ftrack and the
resolver will generate the full path using additional information such as disks
and the project folder attribute. Having the full path is useful in the web
interface where it can be used to start applications directly using protocols 
from the components widget or when clicking on thumbnails.

The status of the resolver service can be found in the diagnostics page:

1. Open ftrack in your favorite browser (Chrome, Firefox or Safari)
2. Go to :menuselection:`System settings --> General Settings --> Diagnostics`

.. figure:: /image/settings_general_settings_diagnostics_page.jpg

    Screenshot of the Diagnostics page.
