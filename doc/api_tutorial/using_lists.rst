..
    :copyright: Copyright (c) 2014 ftrack

.. _developing/legacy/api_tutorial/using_lists:

***********
Using lists
***********

Lists are collections of existing objects in ftrack. When creating a list you
need to specify the type of objects the list accepts. There are two options,
Sequence/Shot/Task or Asset versions. The default is Sequence/Shot/Task.

Create a list for shots in the trailer::

    project = ftrack.getProject('dev_tutorial')

    # Get category for list.
    category = ftrack.getListCategories()[0]

    # Create a list that accepts tasks.
    trailerList = project.createList('trailer', category)

    # Get some shots to add to the list.
    shot1 = ftrack.getShot(['dev_tutorial', '001', '010'])
    shot2 = ftrack.getShot(['dev_tutorial', '001', '020'])
    shot3 = ftrack.getShot(['dev_tutorial', '001', '030'])

    # Add a single shot to the list.
    trailerList.append(shot1)

    # Add several shots to the list at once.
    trailerList.extend([shot2, shot3])

    # Display the names of all shots in the list.
    for shot in trailerList:
        print shot.getName()

Create a review list that can be used for dailies::

    # Create a list that accepts asset versions.
    dailies = project.createList(
        'dailies', category, ftrack.AssetVersion
    )

    version = shot1.getAssets()[0].getVersions()[0]

    # Add an asset version to the list.
    dailies.append(version)

