..
    :copyright: Copyright (c) 2014 ftrack

.. py:currentmodule:: ftrack

.. _developing/legacy/api_tutorial/using_notes:

***********
Using notes
***********

Notes can be created on any :py:class:`Noteable` object using
:py:meth:`~Noteable.createNote`::

    # Get a shot.
    shot = ftrack.getShot(['dev_tutorial', '001', '010'])

    # Note text.
    text = 'This looks great...'

    # Create note.
    note = shot.createNote(text)

Notes can also have different categories::

    # Note text.
    text = 'This also looks great...'

    # Get a category.
    category = ftrack.getNoteCategories()[0]

    # Create note.
    note = shot.createNote(text, category)

