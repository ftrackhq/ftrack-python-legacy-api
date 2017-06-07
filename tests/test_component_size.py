# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack
import os

import ftrack

from .tools import assert_equal


class TestComponentSize(object):
    '''Test component size.'''

    def testCreateFileWithoutSpecifyingSize(self):
        '''Create file component and let ftrack calculate the size.'''
        path = os.path.abspath('./data/bigfile.mov')
        fileComponent = ftrack.createComponent(name='video', path=path)

        assert_equal(
            fileComponent.getSize(),
            18517384,
            'Size of video is not correct.'
        )

    def testCreateSequenceWithoutSpecifyingSize(self):
        '''Create sequence component and let ftrack calculate the size.'''
        path = os.path.abspath('./data/sequence')
        sequenceComponent = ftrack.createComponent(
            name='imagesequence',
            path='{path}/file.%03d.jpg [1-5]'.format(path=path),
            location=None
        )

        assert_equal(
            sequenceComponent.getSize(),
            486220,
            'Size of image sequence is not correct.'
        )

        memberSizes = [94902, 98181, 98510, 96516, 98111]
        for i, member in enumerate(sequenceComponent.getMembers()):
            assert_equal(
                member.getSize(),
                memberSizes[i],
                'Size of member is not correct.'
            )

    def testCreateFileSpecifyingSize(self):
        '''Create file component and specify a size.'''
        path = os.path.abspath('./data/bigfile.mov')
        fileComponent = ftrack.createComponent(
            name='video',
            path=path,
            size=9999,
            location=None
        )

        assert_equal(
            fileComponent.getSize(),
            9999,
            'Size of video is not correct.'
        )

    def testCreateSequenceSpecifyingSize(self):
        '''Create sequence component and specify a size.'''
        path = os.path.abspath('./data/sequence')
        sequenceComponent = ftrack.createComponent(
            name='imagesequence',
            path='{path}/file.%03d.jpg [1-5]'.format(path=path),
            size=5 * 9999,
            location=None
        )

        assert_equal(
            sequenceComponent.getSize(),
            5 * 9999,
            'Size of image sequence is not correct.'
        )

        for member in sequenceComponent.getMembers():
            assert_equal(
                member.getSize(),
                9999,
                'Size of member is not correct.'
            )

    def testCreateFileWithoutSpecifyingSizeOrPath(self):
        '''Create components and let ftrack fail to calculate the size.'''
        fileComponent = ftrack.createComponent(
            name='video',
            path='/mypath/video.mov',
            location=None
        )

        assert_equal(
            fileComponent.getSize(),
            0,
            'Size of video is not correct.'
        )

    def testCreateSequenceWithoutSpecifyingSizeOrPath(self):
        '''Create components and let ftrack fail to calculate the size.'''
        sequenceComponent = ftrack.createComponent(
            name='imagesequence',
            path='/mypath/file_bad.%03d.jpg [1-5]',
            location=None
        )

        assert_equal(
            sequenceComponent.getSize(),
            0,
            'Size of image sequence is not correct.'
        )

        for member in sequenceComponent.getMembers():
            assert_equal(
                member.getSize(),
                0,
                'Size of member is not correct.'
            )

    def testCreateSequenceWithoutMembersSpecifyingSize(self):
        '''Create sequence without members specifying size.'''
        sequenceComponent = ftrack.createComponent(
            name='imagesequence',
            systemType='sequence',
            location=None,
            size=444
        )

        assert_equal(
            sequenceComponent.getSize(),
            444,
            'Size of image sequence is not correct.'
        )

    def testCreateSequenceWithoutMembersWithoutSpecifyingSize(self):
        '''Create sequence without members without specifying size.'''
        sequenceComponent = ftrack.createComponent(
            name='imagesequence',
            systemType='sequence',
            location=None
        )

        assert_equal(
            sequenceComponent.getSize(),
            0,
            'Size of image sequence is not correct.'
        )

    def testGetAndSetSize(self):
        '''Set and get size from a component.'''
        component = ftrack.createComponent()

        assert_equal(component.getSize(), 0, 'Size is not 0')

        component.setSize(2000)

        assert_equal(component.getSize(), 2000, 'Size is not 2000')

        # Make sure we get component from server.
        component = ftrack.Component(component.getId())

        assert_equal(component.getSize(), 2000, 'Size is not 2000')

    def testCreateFileSpecifyingBigSize(self):
        '''Create file component and specify a size over the 32-bit limit.'''
        path = os.path.abspath('./data/bigfile.mov')
        fileComponent = ftrack.createComponent(
            name='video',
            path=path,
            size=3221225472,
            location=None
        )

        assert_equal(
            fileComponent.getSize(),
            3221225472,
            'Size of video is not correct.'
        )
