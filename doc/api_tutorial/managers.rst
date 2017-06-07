..
    :copyright: Copyright (c) 2014 ftrack

.. _developing/legacy/api_tutorial/managers:

********
Managers
********

A manager is a user connected to an entity. The managers also have a type that
can be added in :guilabel:`Settings`. Managers can be created on a project or any other
entity that make up the project hierarchy such as a sequence or shot.

Add a manager for a project::

    project = ftrack.getProject('dev_tutorial')
    user = ftrack.User('username')
    managerType = ftrack.ManagerType('Supervisor')

    # Add the user as a supervisor on the dev_tutorial project.
    manager = project.createManager(user, managerType)

Fetch managers for a project::

    project = ftrack.getProject('dev_tutorial')
    managers = project.getManagers()

Fetch manager types::

    # Fetch all manager types.
    managerTypes = ftrack.getManagerTypes()

    # Fetch using the name of the manager.
    managerType = ftrack.ManagerType('Supervisor')

Delete managers from a project::

    project = ftrack.getProject('dev_tutorial')
    managers = project.getManagers()

    # Delete one of the managers.
    managers[0].delete()