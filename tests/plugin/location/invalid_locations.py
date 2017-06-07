import os
import tempfile

from ftrack import Location, DiskAccessor, IdStructure, ensureLocation


def register(registry, **kw):
    '''Register location.'''
    structure = IdStructure()

    # Add location without accessor plugin
    name = 'location_without_accessor'
    # TODO: Remove need for this line.
    ensureLocation(name)
    location = Location(
        name,
        accessor=None,
        structure=structure,
        priority=2
    )

    registry.add(location)

    # Add location without structure plugin
    name = 'location_without_structure'
    ensureLocation(name)
    prefix = os.path.join(tempfile.gettempdir(), 'ftrack', name)
    accessor = DiskAccessor(prefix=prefix)
    location = Location(
        name,
        accessor=accessor,
        structure=None,
        priority=2
    )

    registry.add(location)

    # Add location without both structure and accessor
    name = 'location_without_structure_and_accessor'
    # TODO: Remove need for this line.
    ensureLocation(name)

    location = Location(
        name,
        accessor=None,
        structure=None,
        priority=2
    )

    registry.add(location)
