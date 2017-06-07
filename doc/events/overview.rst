..
    :copyright: Copyright (c) 2014 ftrack

.. _developing/legacy/events/overview:

********
Overview
********

.. _developing/legacy/events/overview/subscribing_to_events:

Subscribing to events
=====================

To listen to events, you register a function against a subscription using
:py:meth:`ftrack.EVENT_HUB.subscribe <ftrack.EventHub.subscribe>`. The
subscription uses the :ref:`expression <developing/legacy/events/overview/expressions>`
syntax and will filter against each :py:class:`ftrack.Event` instance to
determine if the registered function should receive that event. If the
subscription matches, the registered function will be called with the
:py:class:`ftrack.Event` instance as its sole argument. The
:py:class:`ftrack.Event` instance is a mapping like structure and can be used
like a normal dictionary.

The following example subscribes a function to receive all 'ftrack.update'
events and then print out the entities that were updated::

    import ftrack
    ftrack.setup()

    def myCallback(event):
        '''Event callback printing all new or updated entities.'''
        for entity in event['data'].get('entities', []):
            
            # Print data for the entity.
            print(entity)

    # Subscribe to events with the update topic.
    ftrack.EVENT_HUB.subscribe('topic=ftrack.update', myCallback)

At this point, if you run this, your handler won't yet be processing received
events. In order to do this you have to call the
:py:meth:`~ftrack.EventHub.wait` method::

    # Wait for events to be received and handled.
    ftrack.EVENT_HUB.wait()

You cancel waiting for events by using a system interrupt (:kbd:`Ctrl-C`).
Alternatively, you can specify a *duration* to process events for::

    # Only wait and process events for 5 seconds.
    ftrack.EVENT_HUB.wait(duration=5)

.. note::

    Events are continually received and queued for processing in the background
    as soon as the connection to the server is established. As a result you may
    see a flurry of activity as soon as you call
    :py:meth:`~ftrack.EventHub.wait` for the first time.

.. _developing/legacy/events/overview/subscribing_to_events/subscriber_information:

Subscriber information
----------------------

When subscribing, you can also specify additional information about your
subscriber. This contextual information can be useful when routing events,
particularly when :ref:`targeting events
<developing/legacy/events/overview/publishing_events/targeting_events>`. By default,
the :py:class:`~ftrack.EventHub` will set some default information, but it can
be useful to enhance this. To do so, simply pass in *subscriber* as a dictionary
of data to the :py:meth:`~ftrack.EventHub.subscribe` method::

    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.update',
        myCallback,
        subscriber={
            'id': 'my-unique-subscriber-id',
            'applicationId': 'maya'
        }
    )

.. _developing/legacy/events/overview/subscribing_to_events/sending_replies:

Sending replies
---------------

When handling an event it is sometimes useful to be able to send information
back to the source of the event. For example,
:ref:`developing/events/list/ftrack.location.request-resolve` would expect a
resolved path to be sent back.

You can craft a custom reply event if you want, but an easier way is just to
return the appropriate data from your handler. Any non *None* value will be
automatically sent as a reply::

    def onEvent(event):
        return {'success': True, 'message': 'Cool!'}

    ftrack.EVENT_HUB.subscribe('topic=test-reply', onEvent)

.. seealso::

    :ref:`developing/legacy/events/overview/publishing_events/handling_replies`

Stopping events
---------------

The *event* instance passed to each event handler also provides a method for
stopping the event, :py:meth:`ftrack.Event.stop`.

Once an event has been stopped, no further handlers for that specific event
will be called **locally**. Other handlers in other processes may still be
called.

Combining this with setting appropriate priorities when subscribing to a topic
allows handlers to prevent lower priority handlers running when desired.

    >>> import ftrack
    >>> ftrack.setup()
    >>>
    >>> def callbackA(event):
    ...     '''Stop the event!'''
    ...     print('Callback A')
    ...     event.stop()
    >>>
    >>> def callbackB(event):
    ...     '''Never run.'''
    ...     print('Callback B')
    >>>
    >>> ftrack.EVENT_HUB.subscribe(
    ...     'topic=test-stop-event', callbackA, priority=10
    ... )
    >>> ftrack.EVENT_HUB.subscribe(
    ...     'topic=test-stop-event', callbackB, priority=20
    ... )
    >>> ftrack.EVENT_HUB.publish(ftrack.Event(topic='test-stop-event'))
    >>> ftrack.EVENT_HUB.wait(duration=5)
    Callback A called.

.. _developing/legacy/events/overview/publishing_events:

Publishing events
=================

So far we have looked at listening to events coming from ftrack. However, you
are also free to publish your own events (or even publish relevant ftrack
events).

To do this, simply construct an instance of :py:class:`ftrack.Event` and pass it
to :py:meth:`ftrack.EVENT_HUB.publish <ftrack.EventHub.publish>`::

    event = ftrack.Event(
        topic='my-company.some-topic',
        data={'key': 'value'}
    )
    ftrack.EVENT_HUB.publish(event)

The event hub will automatically add some information to your event before it
gets published, including the *source* of the event. By default the event source
is just the event hub, but you can customise this to provide more relevant
information if you want. For example, if you were publishing from within Maya::

    ftrack.EVENT_HUB.publish(ftrack.Event(
        topic='my-company.some-topic',
        data={'key': 'value'},
        source={
            'applicationId': 'maya'
        }
    ))

Remember that all supplied information can be used by subscribers to filter
events so the more accurate the information the better.

Publish synchronously
---------------------

It is also possible to call :py:meth:`~ftrack.EventHub.publish` synchronously by
passing `synchronous=True`. In synchronous mode, only local handlers will be
called. The result from each called handler is collected and all the results
returned together in a list::

    >>> import ftrack
    >>>
    >>> def callbackA(event):
    ...     return 'A'
    >>>
    >>> def callbackB(event):
    ...     return 'B'
    >>>
    >>> ftrack.EVENT_HUB.subscribe(
    ...     'topic=test-synchronous', callbackA, priority=10
    ... )
    >>> ftrack.EVENT_HUB.subscribe(
    ...     'topic=test-synchronous', callbackB, priority=20
    ... )
    >>> results = ftrack.EVENT_HUB.publish(
    ...     Event(topic='test-synchronous'),
    ...     synchronous=True
    ... )
    >>> print results
    ['A', 'B']

.. _developing/legacy/events/overview/publishing_events/handling_replies:

Handling replies
----------------

When publishing an event it is also possible to pass a callable that will be
called with any :ref:`reply event
<developing/legacy/events/overview/subscribing_to_events/sending_replies>` received in
response to the published event.

To do so, simply pass in a callable as the *onReply* parameter::

    def handleReply(replyEvent):
        print 'Got reply', replyEvent

    ftrack.EVENT_HUB.publish(
        Event(topic='test-reply'),
        onReply=handleReply
    )

.. _developing/legacy/events/overview/publishing_events/targeting_events:

Targeting events
----------------

In addition to subscribers filtering events to receive, it is also possible to
give an event a specific target to help route it to the right subscriber.

To do this, set the *target* value on the event to an :ref:`expression
<developing/legacy/events/overview/expressions>`. The expression will filter against
registered :ref:`subscriber information
<developing/legacy/events/overview/subscribing_to_events/subscriber_information>`.

For example, if you have many subscribers listening for a event, but only want
one of those subscribers to get the event, you can target the event to the
subscriber using its registered subscriber id::

    ftrack.EVENT_HUB.publish(
        ftrack.Event(
            topic='my-company.topic',
            data={'key': 'value'},
            target='id=my-custom-subscriber-id'
        )
    )

.. _developing/legacy/events/overview/expressions:

Expressions
===========

An expression is used to filter against a data structure, returning whether the
structure fulfils the expression requirements. Expressions are currently used
for subscriptions when :ref:`subscribing to events
<developing/legacy/events/overview/subscribing_to_events>` and for targets when
:ref:`publishing targeted events
<developing/legacy/events/overview/publishing_events/targeting_events>`.

The form of the expression is loosely groupings of 'key=value' with conjunctions
to join them.

For example, a common expression for subscriptions is to filter against an event
topic::


    'topic=ftrack.location.component-added'

However, you can also perform more complex filtering, including accessing
nested parameters::

    'topic=ftrack.location.component-added and data.locationId=london'

.. note::

    If the structure being tested does not have any value for the specified
    key reference then it is treated as *not* matching.

You can also use a single wildcard '*' at the end of any value for matching
multiple values. For example, the following would match all events that have a
topic starting with 'ftrack.'::

    'topic=ftrack.*'
