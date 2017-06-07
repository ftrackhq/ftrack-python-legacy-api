# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import sys
import os
import time
import logging
import argparse

# Make ftrack module importable.
# TODO: Remove need for this by setting up test environment properly at a global
# level.
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__name__))))

import ftrack

TOPIC = 'test_event_hub_server_heartbeat'
RECEIVED = []


def callback(event):
    '''Track received messages.'''
    counter = event['data']['counter']
    RECEIVED.append(counter)
    print('Received message {0} ({1} in total)'.format(counter, len(RECEIVED)))


def main(arguments=None):
    '''Publish and receive heartbeat test.'''
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['publish', 'subscribe'])

    namespace = parser.parse_args(arguments)

    logging.basicConfig(level=logging.INFO)
    ftrack.setup()

    messageCount = 100
    sleepTimePerMessage = 1

    if namespace.mode == 'publish':
        print('Sending {0} messages...'.format(messageCount))

        for counter in range(1, messageCount + 1):
            ftrack.EVENT_HUB.publish(
                ftrack.Event(topic=TOPIC, data=dict(counter=counter))
            )
            print('Sent message {0}'.format(counter))

            if counter < messageCount:
                time.sleep(sleepTimePerMessage)

    elif namespace.mode == 'subscribe':
        ftrack.EVENT_HUB.subscribe('topic={0}'.format(TOPIC), callback)
        ftrack.EVENT_HUB.wait(
            duration=(
                ((messageCount - 1) * sleepTimePerMessage) + 15
            )
        )

        if len(RECEIVED) != messageCount:
            print(
                '>> Failed to receive all messages. Dropped {0} <<'
                .format(messageCount - len(RECEIVED))
            )
            return False

    # Give time to flush all buffers.
    time.sleep(5)

    return True


if __name__ == '__main__':
    result = main(sys.argv[1:])
    if not result:
        raise SystemExit(1)
    else:
        raise SystemExit(0)