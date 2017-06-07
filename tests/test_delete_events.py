# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack

from uuid import uuid1 as uuid

from ftrack import EventHub
import ftrack
from .tools import assert_equal


class TestDeleteEvents(object):
    '''Test delete events.'''

    def getTestData(self):
        '''Return tuple with (project, episode, sequence, shot).'''
        project = ftrack.createProject(
            uuid().hex,
            uuid().hex,
            ftrack.getProjectSchemes()[0]
        )
        episode = project.createEpisode(uuid().hex)
        sequence = episode.createSequence(uuid().hex)
        shot = sequence.createShot(uuid().hex)
        return (project, episode, sequence, shot)

    def testDeleteEventContainsAllObjects(self):
        '''Ensure that all deleted objects are included in the event.

        Deletes an episode and verifies that the episode and all its children
        are included in the event.

        '''
        (project, episode, sequence, shot) = self.getTestData()
        eventHub = EventHub()
        eventHub.connect()

        result = {
            'data': None
        }

        def callback(event):
            result['data'] = event['data']

        eventHub.subscribe('topic=ftrack.update', callback)
        episode.delete()
        eventHub.wait(1)
        deletedIds = [episode.getId(), sequence.getId(), shot.getId()]
        idsInEvent = []
        for entity in result['data']['entities']:
            if entity['action'] != 'remove':
                continue
            idsInEvent.append(entity['entityId'])

        assert_equal(
            sorted(deletedIds),
            sorted(idsInEvent),
            'Events were published for all objects.'
        )

    def testDeleteEventContainsCorrectParents(self):
        '''Ensure a delete event contains the correct parent information.

        Deletes a sequence and verifies that the event contains correct parent
        information for the sequence itself and its shot.

        '''
        (project, episode, sequence, shot) = self.getTestData()

        eventHub = EventHub()
        eventHub.connect()

        result = {
            'data': None
        }

        def callback(event):
            '''Event callback.'''
            result['data'] = event['data']

        eventHub.subscribe('topic=ftrack.update', callback)

        def assertEventParents(parents, data, entity):
            '''Compare *parents* to information in *data* for *entity*.'''
            parentIds = [parent.getId() for parent in parents]
            parentIds.append(entity.getId())
            deletedParentIds = []
            for deletedEntity in result['data']['entities']:
                if deletedEntity['entityId'] == entity.getId():
                    deletedParentIds = [
                        parent['entityId'] for parent in deletedEntity['parents']
                    ]

            assert_equal(
                sorted(parentIds),
                sorted(deletedParentIds),
                'Parent ids of deleted object {object} are correct.'.format(
                    object=entity
                )
            )

        sequenceParents = sequence.getParents()
        shotParents = shot.getParents()
        sequence.delete()
        eventHub.wait(1)

        assertEventParents(sequenceParents, result['data'], sequence)
        assertEventParents(shotParents, result['data'], shot)
