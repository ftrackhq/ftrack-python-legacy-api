import os
import tempfile

import ftrack


def createTestLocation(name, priority=10):
    '''Create, configure and register a location for testing purposes.

    Uses a *DiskAccessor* with temporary storage and an *IdStructure*.

    '''
    location = ftrack.LOCATION_PLUGINS.get(name)

    if not location:
        # Create a disk accessor with *temporary* storage
        tempdir = tempfile.gettempdir()
        prefix = os.path.join(tempdir, name)
        if not os.path.exists(prefix):
            os.mkdir(prefix)

        accessor = ftrack.DiskAccessor(prefix=prefix)

        # Create folder structure based on component ids.
        structure = ftrack.IdStructure()

        # Create a location object
        location = ftrack.ensureLocation(name)
        location = ftrack.Location(
            name,
            accessor=accessor,
            structure=structure,
            priority=priority
        )

        ftrack.LOCATION_PLUGINS.add(location)

    return location
