..
    :copyright: Copyright (c) 2014 ftrack

.. py:currentmodule:: ftrack

.. _developing/legacy/api_tutorial/using_statuses:

**************
Using statuses
**************

Changing task status
====================

The workflow schema defines which task statuses are available for a project::

    project = ftrack.getProject('dev_tutorial')

    # Get all task statuses available on this project.
    statuses = project.getTaskStatuses()

To set the status call :py:meth:`Task.setStatus` on the task::

    # Get a task.
    shot = ftrack.getShot(['dev_tutorial', '001', '010'])
    task = shot.getTasks()[0]

    # Change status.
    task.setStatus(statuses[1])

There can also be overrides that define statuses available for individual task
types in case they differ from the standard workflow::

    taskType = task.getType()

    # Get task statuses for a specific task type.
    statuses = project.getTaskStatuses(taskType)

    # Change status.
    task.setStatus(statuses[0])

Changing asset version status
=============================

The workflow schema defines what statuses are available for
:term:`asset versions <asset version>`::

    project = ftrack.getProject('dev_tutorial')

    # Get all version statuses available on this project.
    statuses = project.getVersionStatuses()

    # Publish a version.
    shot = ftrack.getShot(['dev_tutorial', '001', '010'])
    version = shot.getAssets()[0].getVersions()[0]

    # Change status.
    version.setStatus(statuses[-1])

