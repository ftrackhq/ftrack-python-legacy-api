..
    :copyright: Copyright (c) 2014 ftrack

.. py:currentmodule:: ftrack

.. _developing/legacy/api_tutorial/using_tasks:

***********
Using tasks
***********

To retrieve all the tasks for a current user, use the :py:meth:`User.getTasks`
method::

    # Get current user.
    user = ftrack.getUser(getpass.getuser())

    # Get all tasks for current user.
    tasks = user.getTasks()
    for task in tasks:
        print task.getName()

It is also possible to fetch a filtered list of tasks::

    # Get only tasks that are in progress.
    inProgress = user.getTasks(states=[ftrack.IN_PROGRESS])

