..
    :copyright: Copyright (c) 2014 ftrack

.. py:currentmodule:: ftrack

.. _developing/legacy/api_tutorial/logging_time:

************
Logging time
************

It is possible to log time using the :term:`API`.

First retrieve a task::

    shot = ftrack.getShot(['dev_tutorial', '001', '010'])
    task = shot.getTasks()[0]

The user must be assigned to the task in order to log time::

    import getpass

    currentUser = ftrack.User(getpass.getuser())
    task.assignUser(currentUser)

Log four hours of work to a task today using
:py:meth:`createTimelog`::

    ftrack.createTimelog(
        start=datetime.datetime.now(),
        duration=4 * 60 * 60,
        contextId=task.getId()
    )

Retrieve timelogs from a task using :py:meth:`Task.getTimelogs`::

    print task.getTimelogs()
