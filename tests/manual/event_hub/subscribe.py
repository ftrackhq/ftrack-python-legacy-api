# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import sys
import os
import logging
import argparse

# Make ftrack module importable.
# TODO: Remove need for this by setting up test environment properly at a global
# level.
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
)

import ftrack


def onEvent(event):
    '''Handle receive *event*.'''
    logger = logging.getLogger('ftrack.test.manual.event_hub.onEvent')
    logger.info('Received event: {0}'.format(event))


def main(arguments=None):
    '''Connect to event server and send an event.'''
    parser = argparse.ArgumentParser()

    # Allow setting of logging level from arguments.
    loggingLevels = {}
    for level in (
        logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARNING,
        logging.ERROR, logging.CRITICAL
    ):
        loggingLevels[logging.getLevelName(level).lower()] = level

    parser.add_argument(
        '-v', '--verbosity',
        help='Set the logging output verbosity.',
        choices=loggingLevels.keys(),
        default='info'
    )

    namespace = parser.parse_args(arguments)

    logging.basicConfig(level=loggingLevels[namespace.verbosity])
    logger = logging.getLogger('ftrack.test.manual.event_hub.subscribe')

    ftrack.setup()

    # Override timeout for auto-reconnect.
    ftrack.EVENT_HUB._autoReconnectAttempts = 5

    ftrack.EVENT_HUB.subscribe('topic=*', onEvent)

    logger.info('Listening for events (use Ctrl-C to stop).')
    try:
        ftrack.EVENT_HUB.wait()
    except KeyboardInterrupt:
        logger.info('User aborted process with interrupt.')


if __name__ == '__main__':
    raise SystemExit(main())
