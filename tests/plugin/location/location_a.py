
import os
import tempfile

from ftrack import Location, DiskAccessor, IdStructure, ensureLocation


def register(registry, **kw):
    '''Register location.'''
    name = 'location_a'

    # TODO: Remove need for this line.
    ensureLocation(name)

    prefix = os.path.join(tempfile.gettempdir(), 'ftrack', name)
    accessor = DiskAccessor(prefix=prefix)
    structure = IdStructure()
    location = Location(
        name,
        accessor=accessor,
        structure=structure,
        priority=1
    )

    registry.add(location)
