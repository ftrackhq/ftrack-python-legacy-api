..
    :copyright: Copyright (c) 2014 ftrack

.. _developing/legacy/api_tutorial/querying:

********
Querying
********

Projects
========

All projects can be fetched using :py:func:`ftrack.getProjects`::

    projects = ftrack.getProjects()

    for project in projects:
        print project.getName()

Individual projects can also be fetched using their short name (code)::

    project = ftrack.getProject('dev_tutorial')

Or their unique id::

    # Get the unique id from the project.
    projectId = project.getId()

    # Fetch the project again at a later stage using the id.
    project = ftrack.Project(id=projectId)

Objects
=======

All object classes in ftrack inherit the same base class,
:py:class:`ftrack.FTObject`, that provides common functionality.

For each example, assume a shot has been retrieved::

    shot = ftrack.getShot(['dev_tutorial', '001', '050'])

Generic get and set
-------------------

.. code-block:: python

    # Get name.
    print shot.get('name')

    # Set name.
    shot.set('name', '060')

Retrieving by unique id
-----------------------

.. code-block:: python

    # Get the unique id from the shot.
    shotId = shot.getId()

    # Fetch the shot again at a later stage using the id.
    shot = ftrack.Shot(id=shotId)

Retrieving parents
------------------

.. code-block:: python

    # Get sequence.
    sequence = shot.getParent()

    # Get all parents.
    hierarchy = shot.getParents()

    # Project should be the last one.
    project = hierarchy[-1]
