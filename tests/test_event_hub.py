# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os
import time
import subprocess
import sys

from nose.plugins.attrib import attr

from ftrack import EventHub, Event
from .tools import ok_, assert_equal, capture_logging
from .constant import VERY_SLOW


class MockClass(object):
    '''Mock class for testing.'''

    def method(self):
        '''Mock method for testing.'''


def mockFunction():
    '''Mock function for testing.'''


class MockConnection(object):
    '''Mock connection for testing.'''

    @property
    def connected(self):
        '''Return whether connected.'''
        return True

    def close(self):
        '''Close mock connection.'''
        pass


def assert_callbacks(hub, callbacks):
    '''Assert hub has exactly *callbacks* subscribed.'''
    if len(hub._subscribers) != len(callbacks):
        raise AssertionError(
            'Number of subscribers ({0}) != number of callbacks ({1})'
            .format(len(hub._subscribers), len(callbacks))
        )

    for index, subscriber in enumerate(hub._subscribers):
        if subscriber.callback != callbacks[index]:
            raise AssertionError(
                'Callback at {0} != subscriber callback at same index.'
                .format(index)
            )


class TestEventHub(object):
    '''Test event hub.'''

    def __init__(self):
        '''Initialise test.'''

    def setUp(self):
        '''Perform per test setup.'''

    def tearDown(self):
        '''Perform per test teardown.'''

    def testSubscribe(self):
        '''Subscribe to topics.'''
        eventHub = EventHub()
        eventHub.connect()

        called = {'a': False, 'b': False}

        def callbackA(event):
            called['a'] = True

        def callbackB(event):
            called['b'] = True

        eventHub.subscribe('topic=test-subscribe', callbackA)
        eventHub.subscribe('topic=test-subscribe-other', callbackB)

        eventHub.publish(Event(topic='test-subscribe'))
        eventHub.wait(2)

        assert_equal(called, {'a': True, 'b': False})

    def testUnsubscribe(self):
        '''Unsubscribe a specific callback.'''
        eventHub = EventHub()
        eventHub.connect()

        def callbackA(event):
            pass

        def callbackB(event):
            pass

        identifierA = eventHub.subscribe('topic=test', callbackA)
        identifierB = eventHub.subscribe('topic=test', callbackB)

        assert_callbacks(
            eventHub, [eventHub._handleReply, callbackA, callbackB]
        )

        eventHub.unsubscribe(identifierA)

        # Unsubscribe requires confirmation event so wait here to give event a
        # chance to process.
        time.sleep(5)

        assert_callbacks(
            eventHub, [eventHub._handleReply, callbackB]
        )

    def testPublishFailsGracefully(self):
        '''Log failed publish rather than raise error.'''
        eventHub = EventHub()
        eventHub.connect()

        # Mock connection to force error.
        eventHub._connection = MockConnection()

        event = Event(topic='a-topic', data=dict(status='fail'))
        with capture_logging() as records:
            eventHub.publish(event)

        expected = 'Error sending event {0}.'.format(event)
        messages = [record.getMessage().strip() for record in records]
        ok_(expected in messages, 'Expected log message missing in output.')

    @attr(speed=VERY_SLOW)
    def testServerHeartbeatResponse(self):
        '''Maintain connection by responding to server heartbeat request.'''
        fixturePath = os.path.join(os.path.dirname(__file__), 'fixture')

        # Start subscriber that will listen for all three messages.
        subscriber = subprocess.Popen([
            sys.executable,
            os.path.join(fixturePath, 'event_hub_server_heartbeat.py'),
            'subscribe'
        ])

        # Give subscriber time to connect to server.
        time.sleep(10)

        # Start publisher to publish three messages.
        publisher = subprocess.Popen([
            sys.executable,
            os.path.join(fixturePath, 'event_hub_server_heartbeat.py'),
            'publish'
        ])

        publisher.wait()
        subscriber.wait()

        assert_equal(subscriber.returncode, 0)

    def testStopEvent(self):
        '''Stop processing of subsequent local handlers when stop flag set.'''
        eventHub = EventHub()
        eventHub.connect()

        called = {
            'a': False,
            'b': False,
            'c': False
        }

        def callbackA(event):
            called['a'] = True

        def callbackB(event):
            called['b'] = True
            event.stop()

        def callbackC(event):
            called['c'] = True

        eventHub.subscribe('topic=test', callbackA, priority=50)
        eventHub.subscribe('topic=test', callbackB, priority=60)
        eventHub.subscribe('topic=test', callbackC, priority=70)

        assert_callbacks(
            eventHub, [eventHub._handleReply, callbackA, callbackB, callbackC]
        )

        eventHub.publish(Event(topic='test'))
        eventHub.wait(2)

        assert_equal(called, {
            'a': True,
            'b': True,
            'c': False
        })

    def testSynchronousPublish(self):
        '''Publish event synchronously and collect results.'''
        eventHub = EventHub()
        eventHub.connect()

        def callbackA(event):
            return 'A'

        def callbackB(event):
            return 'B'

        def callbackC(event):
            return 'C'

        eventHub.subscribe('topic=test', callbackA, priority=50)
        eventHub.subscribe('topic=test', callbackB, priority=60)
        eventHub.subscribe('topic=test', callbackC, priority=70)

        assert_callbacks(
            eventHub, [eventHub._handleReply, callbackA, callbackB, callbackC]
        )

        # Give time for subscriptions to process and subscribers to be
        # activated as bypassing normal event routine.
        time.sleep(5)

        results = eventHub.publish(
            Event(topic='test'), synchronous=True
        )

        assert_equal(
            results, ['A', 'B', 'C']
        )
