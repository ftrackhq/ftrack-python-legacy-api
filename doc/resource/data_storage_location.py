import logging

from ftrack import (
    ensureLocation, Location, IdStructure, DiskAccessor, Registry
)


def register(registry, **kw):
    '''Register custom location.'''

    logger = logging.getLogger(
        'ftrack_plugin:data_storage_location.register'
    )

    # Validate that registry is an instance of ftrack.Registry. If not,
    # assume that register is being called from a new or incompatible API and
    # return without doing anything.
    if not isinstance(registry, Registry):
        logger.debug(
            'Not subscribing plugin as passed argument {0!r} is not an '
            'ftrack.Registry instance.'.format(registry)
        )
        return

    locationName = 'custom.location'

    # Ensure location is registered in the database.
    ensureLocation(locationName)

    # Create the new location plugin.
    location = Location(
        locationName,

        # Use an id based structure.
        structure=IdStructure(),

        # The location will be a local disk.
        accessor=DiskAccessor(prefix='/mnt/demodisk/'),

        # High priority, all new publishes should go here.
        priority=1
    )

    # Register the location plugin.
    registry.add(location)
