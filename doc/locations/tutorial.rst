..
    :copyright: Copyright (c) 2014 ftrack

********
Tutorial
********

This tutorial is a walkthrough on how you interact with Locations using the 
ftrack :ref:`API <developing/legacy/api_reference>`. Before you read this tutorial,
make sure you familiarize yourself  with the location concepts by reading
:ref:`using/locations`.

All examples assume you are using Python 2.x, have the :py:mod:`ftrack` module 
imported and that :py:func:`ftrack.setup` has been called. 

.. code-block:: python

    import ftrack
    ftrack.setup()


.. _creating-locations:

Creating locations
==================

Locations consist of two parts, an entity in the database on the ftrack server 
and an optional plugin loaded through the ftrack client
:ref:`API <developing/legacy/api_reference>`. The two are paired  at runtime based on
their name.

If a plugin for a location is not found at runtime, you will still be able to 
interact with the location metadata, but will not be able to use that location 
to manage components (for example, adding a component to a location) in the 
session.

Locations can be created on the server using the :py:func:`ftrack.createLocation`
function, which will return a :py:class:`Location` instance. An error will be 
raised if a location with the given name already exists.

.. code-block:: python

    # Create a new location entity
    location = ftrack.createLocation('test.location')

.. note:: 
    Location names beginning with ``ftrack.`` are reserved for internal use. Do
    not use this prefix for your location names.

To create a location only if it doesn't already exist use the convenience 
function :py:func:`ftrack.ensureLocation`. This will return either an existing 
matching location or a newly created one.

.. code-block:: python

    # Get a location, creating it if it doesn't exist
    location = ftrack.ensureLocation('test.location')

At this point you have created a location in the database and have an instance 
to reflect that. However, the location cannot be used in this session to manage 
data unless it has a corresponding plugin initialized.

A plugin is simple to write and is often just a binding together of various 
functionality into one instance. Here is an example of defining and manually 
registering a Location plugin

.. code-block:: python

    # Create a disk accessor with *temporary* storage
    import tempfile
    prefix = tempfile.mkdtemp()    
    accessor = ftrack.DiskAccessor(prefix=prefix)

    # Use classic structure with paths generated to support a typical studio structure.
    structure = ftrack.ClassicStructure()

    # Create a location instance
    location = ftrack.Location(
        'test.location',
        accessor=accessor,
        structure=structure,
        priority=30
    )

    # Add the instance to the registry
    ftrack.LOCATION_PLUGINS.add(location)

Now that the plugin is created and added to the registry, any new Location 
instances in the same session with the matching name ``test.location`` will 
automatically receive the attributes specified in the plugin.

To learn more about how to find and configure location plugins automatically in 
a session, see :ref:`using/locations/administration`.

Retrieving locations
====================

You can obtain a :py:class:`Location` object either by id or by name as in the 
example below.

.. code-block:: python

    locationId = location.getId()
    location = ftrack.Location(locationId)

    locationName = 'test.location'
    location = ftrack.Location(locationName)


To retrieve all existing locations which are saved on the ftrack server, call 
the function :py:func:`ftrack.getLocations`. It will return a list of 
:py:class:`Location` objects.

.. code-block:: python

    # List all locations
    locations = ftrack.getLocations()
    for location in locations:
        print location.getName()

.. note:: 
    The locations ``ftrack.unmanaged``, ``ftrack.connect`` and 
    ``ftrack.review`` are used internally for backwards compatibility,
    **ftrackconnect** and **ftrackreview** integration.

Using components with locations
===============================

To run the examples in this section, we first need to create multiple test 
locations. Download the python file 
:download:`create_test_location.py </resource/create_test_location.py>` and 
place it in the same directory from which you are running the interpreter.
The file contains a function, ``createTestLocation``, which is a modified version 
of the example in :ref:`creating-locations`. After the file has been 
downloaded, import the function and create two new locations.

.. code-block:: python

    from create_test_location import createTestLocation
    createTestLocation('test.location.a', priority=10)
    createTestLocation('test.location.b', priority=20)

The Locations :ref:`API <developing/legacy/api_reference>` tries to use sane defaults
to stay out of your way. When creating :term:`components <component>`, a
location is automatically  picked (using :py:func:`ftrack.pickLocation`).

.. code-block:: python

    import tempfile
    (_, componentPath) = tempfile.mkstemp(suffix='.txt')
    component = ftrack.createComponent(path=componentPath)

    # Check which location was picked 
    componentLocation = component.getLocation()
    print 'Component created in location:', componentLocation.getName()

If you are following along with the examples, location ``test.location.a`` 
should be picked, since it has the lowest priority value. If no other locations 
are configured, the component is created in the special ``ftrack.origin`` 
location.

You can specify a specific location when creating the :py:class:`Component` by 
passing it to the constructor as the :py:data:`location` keyword argument. If 
you set the location to ``None``, the component will only be present in the 
origin location.

.. code-block:: python

    componentInOrigin = ftrack.createComponent(path=componentPath, location=None)

    # Should print the ``ftrack.origin`` location
    print componentInOrigin.getLocation().getName()

After we have created a :term:`component` in a location, it can be added to 
another location by calling :py:func:`location.addComponent`.

.. code-block:: python

    locationB = ftrack.ensureLocation('test.location.b')
    componentInLocationB = locationB.addComponent(component)

The returned ``componentInLocationB`` is a new :py:class:`Component` instance, 
configured with attributes relevant to ``locationB``.

When adding a :term:`component` to a location, the file(s) will automatically 
be transferred to the location. If you prefer to do this manually, you can set
:py:data:`manageData` to :py:data:`False`.

.. code-block:: python

    # Create a component, pick location automatically
    component = ftrack.createComponent(path=componentPath)

    # Create a test location, *test.location.c*
    locationC = createTestLocation('test.location.c')

    # Add the component to the location, but assume data is already transferred
    componentInLocationC = locationC.addComponent(component, manageData=False)


The locations system is designed to help avoid having to deal with filesystem
paths directly. This is particularly important when you consider that a number
of locations won't provide any direct filesystem access (such as cloud storage).

However, it is useful to still be able to get a filesystem path from locations
that support them (typically those configured with a
:py:class:`~ftrack.DiskAccessor`). For example, you might need to pass a
filesystem path to another application or perform a copy using a faster
protocol.

To retrieve the path if available, use :py:meth:`Component.getFilesystemPath`.

The example below copies the data manually for the component in the last
example.

.. code-block:: python

    import os
    import shutil

    sourcePath = component.getFilesystemPath()
    targetPath = componentInLocationC.getFilesystemPath()

    os.makedirs(os.path.dirname(targetPath))
    shutil.copy(sourcePath, targetPath)

.. note::
    If a filesystem path could not be determined then None is returned from
    :py:meth:`Component.getFilesystemPath`

To remove a component from a location, simply call the 
:py:meth:`location.removeComponent` method.

.. code-block:: python
    
    componentId = component.getId()
    locationC.removeComponent(componentId, manageData=False)

Obtain component availability
=============================

Components in locations have a notion of availability. For regular components,
consisting of a single file, the availability would be either 0 if the 
component is unavailable or 100 percent if the component is available in the 
location. Composite components, like image sequences, have an availability 
which is proportional to the amount of child components that have been added to 
the location. 

For example, an image sequence might currently be in a state of being 
transferred to :py:data:`test.location`. If half of the images are transferred, 
we might feel can start working with the sequence. We can check this using the 
method :py:meth:`location.getComponentAvailability`.

.. code-block:: python

    availability = location.getComponentAvailability(componentId)
    if availability >= 50:
        print 'Component "{0}" is available in "{1}"'.format(
            componentId,
            location.getName()
        )


To check in which locations a component is available, call the method 
:py:meth:`component.getAvailability`.
 
.. code-block:: python

    availabilities = component.getAvailability()

    for locationId, availability in availabilities.iteritems():
        location = ftrack.Location(locationId)
        print location.getName(), availability

If you want to limit the search to specific locations, 
you can specify which using the :py:data:`locationIds` argument. 

.. seealso::
    :py:func:`ftrack.getComponentAvailability`

Location events
===============

If you want to receive event notifications when components are added to or 
removed from locations, you can subscribe to the topics published. To subscribe 
to the events you would call :py:func:`ftrack.EVENT_HUB.subscribe` with either
:py:data:`ftrack.COMPONENT_ADDED_TO_LOCATION_TOPIC` or 
:py:data:`ftrack.COMPONENT_REMOVED_FROM_LOCATION_TOPIC` and the callback you 
want to be run.

In this example we will set up a callback which automatically transfers a 
component added to ``test.location.a``, to ``test.location.b``. We create the 
locations as before using the ``createTestLocation`` function defined in 
:download:`create_test_location.py </resource/create_test_location.py>`.

.. literalinclude:: /resource/locations_event_example.py
    :language: python


To test the functionality we need to trigger the event. Keep the process 
running and open up a new python interpreter to run the test in. The following 
example creates a component in the source location, sleeps for a few seconds 
and then checks if it is available in the target location.

.. literalinclude:: /resource/locations_event_test.py
    :language: python
