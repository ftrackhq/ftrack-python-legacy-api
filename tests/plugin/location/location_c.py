# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack

import os
import tempfile

from ftrack import MemoryLocation, DiskAccessor, IdStructure, ensureLocation


def register(registry, **kw):
    '''Register location.'''
    name = 'location_c'

    # TODO: Remove need for this line.
    ensureLocation(name)

    prefix = os.path.join(tempfile.gettempdir(), 'ftrack', name)
    accessor = DiskAccessor(prefix=prefix)
    structure = IdStructure()
    location = MemoryLocation(
        name,
        accessor=accessor,
        structure=structure,
        priority=20
    )

    registry.add(location)
