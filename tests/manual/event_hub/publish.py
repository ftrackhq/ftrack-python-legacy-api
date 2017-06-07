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


def main(arguments=None):
    '''Connect to event server and send event.'''
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
    logger = logging.getLogger('ftrack.test.manual.event_hub.publish')

    ftrack.setup()

    event = ftrack.Event(
        topic='ftrack.test.topic',
        data=dict(message='hello there.')
    )

    logger.info('Publishing event: {0}'.format(event))
    ftrack.EVENT_HUB.publish(event)
    ftrack.EVENT_HUB.wait(2)


if __name__ == '__main__':
    raise SystemExit(main())
