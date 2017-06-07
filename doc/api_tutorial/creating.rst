..
    :copyright: Copyright (c) 2014 ftrack

.. py:currentmodule:: ftrack

.. _developing/legacy/api_tutorial/creating:

********
Creating
********

Projects
========

Projects can be created using :py:func:`ftrack.createProject`. When creating a
project, a workflow schema must be specified. A workflow schema describes the
statuses and types that can be used for the project. Due to the complexity of
workflow schemas, they can currently only be created in the web interface::

    # Get the first available workflow schema.
    workflowSchema = ftrack.getProjectSchemes()[0]

    # Create the project.
    project = ftrack.createProject(
        'Development Tutorial',   # Display name used in interfaces.
        'dev_tutorial',           # Short name used in scripts.
        workflowSchema
    )

Objects
=======

Objects make up the project hierarchy and can be customized from the ftrack web
interface.

A sequence can be created under a project using
:py:meth:`Project.create`::

    sequence = project.create('Sequence', '001')

And shots can be created for the sequence in the same way.

.. note::

    Behind the scenes sequences and shots are just special
    :py:class:`Tasks <Task>` hence the reference to '**Task**.createShot' above.

.. code-block:: python

    # Create five shots for the sequence.
    for index in range(10, 60, 10):
        sequence.create('Shot', '{0:03d}'.format(index))

Tasks
=====

Tasks can be created on any :py:class:`BaseObject` object using
:py:meth:`~BaseObject.createTask` or using :py:meth:`~BaseObject.create`. They
need to have a type and a status which are defined by the project workflow
schema::

    # Grab a task type from project workflow.
    taskType = project.getTaskTypes()[0]

    # Grab a task status that is valid according to the workflow and task type.
    taskStatus = project.getTaskStatuses(taskType)[0]

    # Create a task on the project.
    project.create('Task', 'a task', taskStatus, taskType)

    # Create a task on a shot.
    shot = ftrack.getFromPath(['dev_tutorial', '001', '010'])
    shot.create('Task', 'a shot task', taskStatus, taskType)

