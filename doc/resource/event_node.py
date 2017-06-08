# :coding: utf-8

import argparse
import logging
import sys

import ftrack


def main(arguments=None):
    '''Event node.

    Discover event plugins on the :envvar:`FTRACK_EVENT_PLUGIN_PATH` and load
    them to subscribe to events.

    Then process events until manually stopped.

    '''
    if arguments is None:
        arguments = []

    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--verbosity',
        help='Set logging verbosity',
        choices=['debug', 'info', 'warning', 'error', 'critical'],
        default='info'
    )
    namespace = parser.parse_args(arguments)

    # Configure logging with verbosity level specified by arguments.
    logging.basicConfig(level=getattr(logging, namespace.verbosity.upper()))

    # Connect to event server and discover local event plugins to subscribe to
    # events.
    ftrack.setup()

    # Run until interrupted.
    ftrack.EVENT_HUB.wait()


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
