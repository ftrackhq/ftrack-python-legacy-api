# :coding: utf-8

import platform as _platform
import logging

import ftrack

TOPIC = 'ftrack.location.request-resolve'


class ComponentInLocationPathResolver(object):
    '''Resolve the filesystem path of a component in a specific location.'''

    def __init__(self, name='ftrack.componentInLocationPathResolver',
                 priority=50):
        '''Initialise resolver with *name* and *priority*.'''
        self._name = name
        self._priority = priority
        super(ComponentInLocationPathResolver, self).__init__()

    def getName(self):
        '''Return name.'''
        return self._name

    def getPriority(self):
        '''Return priority.'''
        return self._priority

    def handle(self, event):
        '''Handle published *event*.

        event['data'] should contain:

            * componentId - The id of the component to resolve for.
            * locationName - Name of the location to resolve for. Can be None to
                             indicate location should be determined
                             automatically.
            * platform - A string representing the platform to resolve for.
                         Can be either 'Windows' or 'Linux'.

        '''
        if event.topic != TOPIC:
            # Only interested in specific topic.
            return

        # Extract useful information from passed event.
        componentId = event['data']['componentId']

        platform = event['data']['platform']
        if platform and platform != _platform.system():
            # Don't resolve paths for other platforms.
            return

        locationName = event['data'].get('locationName', None)
        if not locationName:
            # Pick a suitable location if none was passed.
            location = ftrack.pickLocation(componentId)
            if location is not None:
                locationName = location.getName()

        if not locationName:
            return

        try:
            # Attempt to resolve to full filesystem path using locally
            # available location plugins.
            location = ftrack.Location(locationName)
            component = location.getComponent(componentId)
            resolvedPath = component.getFilesystemPath()

        except ftrack.FTrackError:
            return

        # Return data to send as reply event.
        return {'path': resolvedPath}


def register(registry, **kw):
    '''Register resolver plugin.'''

    logger = logging.getLogger(
        'ftrack_plugin:resolver.register'
    )

    # Validate that registry is an instance of ftrack.Registry. If not,
    # assume that register is being called from a new or incompatible API and
    # return without doing anything.
    if not isinstance(registry, ftrack.Registry):
        logger.debug(
            'Not subscribing plugin as passed argument {0!r} is not an '
            'ftrack.Registry instance.'.format(registry)
        )
        return

    plugin = ComponentInLocationPathResolver()
    ftrack.EVENT_HUB.subscribe('topic={0}'.format(TOPIC), plugin.handle)
    registry.add(plugin)
