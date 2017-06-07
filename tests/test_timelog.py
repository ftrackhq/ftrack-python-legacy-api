# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import datetime
import uuid
import getpass

import ftrack
from .tools import assert_equal, ok_, assert_raises_regexp
import ftestutil


class TestTimelog():
    '''Test timelogs.'''

    def testCreateTimelog(self):
        '''Create a timelog.'''
        start = datetime.datetime.now() - datetime.timedelta(hours=-1)
        start = start.replace(microsecond=0)
        duration = 123
        name = uuid.uuid1().hex
        comment = uuid.uuid1().hex
        timelog = ftrack.createTimelog(
            start=start, duration=duration, name=name, comment=comment
        )
        assert_equal(start, timelog.get('start'), 'Start is correct')
        assert_equal(duration, timelog.get('duration'), 'Duration is correct')
        assert_equal(name, timelog.get('name'), 'Name is correct')
        assert_equal(comment, timelog.get('comment'), 'Comment is correct')
        assert_equal(None, timelog.get('context_id'), 'Context is None')

        user = ftrack.getUser(getpass.getuser())
        assert_equal(timelog.get('user_id'), user.getId(), 'User is correct')

    def testDeleteTimelog(self):
        '''Delete a timelog.'''
        timelog = ftrack.createTimelog(
            start=datetime.datetime.now(), duration=0, name='My log'
        )
        timelog.delete()

        with assert_raises_regexp(ftrack.FTrackError, 'timelog was not found'):
            ftrack.Timelog(timelog.getId())

    def testUpdateTimelog(self):
        '''Update timelog.'''
        timelog = ftrack.createTimelog(
            start=datetime.datetime.now(), duration=0, name='My log'
        )

        assert_equal(0, timelog.get('duration'), 'Duration is 0')
        timelog.set('duration', 100)
        assert_equal(100, timelog.get('duration'), 'Duration is 100')

    def testGetTimelogsFromUser(self):
        '''Get timelogs from user.'''
        user = ftrack.getUser(getpass.getuser())
        timelogIds = []

        for index in range(1, 5):
            timelog = ftrack.createTimelog(
                start=datetime.datetime.now(), duration=index, name='My log'
            )
            timelogIds.append(timelog.getId())

        timelogs = user.getTimelogs()
        serverTimelogIds = [timelog.getId() for timelog in timelogs]
        for timelogId in timelogIds:
            ok_(timelogId in serverTimelogIds, 'Timelog is present in list')

        for timelog in timelogs:
            assert_equal(
                timelog.get('user_id'), user.getId(), 'User is correct'
            )

    def testGetTimelogsFromContext(self):
        '''Get timelogs from context.'''
        project = ftestutil.createProject()
        task = ftestutil.createTasks(parent=project)
        timelogIds = []

        for index in range(1, 5):
            timelog = ftrack.createTimelog(
                start=datetime.datetime.now(), duration=index, contextId=task
            )
            timelogIds.append(timelog.getId())

        timelogs = task.getTimelogs()
        serverTimelogIds = [timelog.getId() for timelog in timelogs]
        for timelogId in timelogIds:
            ok_(timelogId in serverTimelogIds, 'Timelog is present in list')

        timelog = ftrack.createTimelog(
            start=datetime.datetime.now(), duration=0, contextId=project
        )
        timelogs = project.getTimelogs()
        ok_(len(timelogs) == 1, 'Found one timelog')
        assert_equal(
            timelogs[0].getId(),
            timelog.getId(),
            'Found the correct timelog.'
        )

    def testFilterTimelogsByDate(self):
        '''Filter timelogs by date.'''
        project = ftestutil.createProject()
        task = ftestutil.createTasks(parent=project)

        for index in range(1, 5):
            ftrack.createTimelog(
                start=datetime.datetime.now(), duration=index, contextId=task
            )

        for index in range(1, 5):
            ftrack.createTimelog(
                start=datetime.datetime.now() + datetime.timedelta(days=3),
                duration=index,
                contextId=task
            )

        timelogs = task.getTimelogs()

        assert_equal(
            len(timelogs),
            8,
            '8 timelogs were found'
        )

        timelogs = task.getTimelogs(
            start=datetime.datetime.now() + datetime.timedelta(days=2)
        )

        assert_equal(
            len(timelogs),
            4,
            '4 timelogs were found'
        )

        timelogs = task.getTimelogs(
            start=datetime.datetime.now() + datetime.timedelta(days=2),
            end=datetime.datetime.now() + datetime.timedelta(days=4)
        )

        assert_equal(
            len(timelogs),
            4,
            '4 timelogs were found'
        )

        timelogs = task.getTimelogs(
            start=datetime.datetime.now() + datetime.timedelta(days=4),
            end=datetime.datetime.now() + datetime.timedelta(days=5)
        )

        assert_equal(
            len(timelogs),
            0,
            '0 timelogs were found'
        )

    def testTimelogsAreSorted(self):
        '''Timelogs should be sorted by start date.'''
        project = ftestutil.createProject()

        for index in range(1, 3):
            ftrack.createTimelog(
                start=datetime.datetime.now() + datetime.timedelta(days=index),
                duration=index,
                contextId=project
            )

        timelogs = project.getTimelogs()
        ok_(
            timelogs[0].get('start') > timelogs[1].get('start'),
            'Timelogs are sorted correctly'
        )

    def testGetTimelogsIncludeChildrenForProject(self):
        '''Test get timelogs on project descendants.'''
        project = ftestutil.createProject()
        total = 10
        tasks = ftestutil.createTasks(project, total)

        for index, task in enumerate(tasks):
            ftrack.createTimelog(
                start=datetime.datetime.now() + datetime.timedelta(days=index),
                duration=index,
                contextId=task
            )

        timelogs = project.getTimelogs()
        assert_equal(
            len(timelogs),
            0,
            '0 timelogs were found'
        )

        timelogs = project.getTimelogs(includeChildren=True)
        assert_equal(
            len(timelogs),
            total,
            '{0} timelogs were found'.format(total)
        )

        ftrack.createTimelog(
            start=datetime.datetime.now(),
            duration=1,
            contextId=project
        )
        total += 1

        timelogs = project.getTimelogs()
        assert_equal(len(timelogs), 1, '1 timelogs were found')

        timelogs = project.getTimelogs(includeChildren=True)
        assert_equal(len(timelogs), total, '{0} timelogs were found'.format(total))


    def testGetTimelogsIncludeChildrenForObjects(self):
        '''Test getting timelogs on various objects in a project hierarchy.'''
        project = ftestutil.createProject()
        sequence = project.createSequence(uuid.uuid1().hex)
        shotOne = sequence.createShot(uuid.uuid1().hex)
        shotTwo = sequence.createShot(uuid.uuid1().hex)
        tasksOne = ftestutil.createTasks(shotOne, 5)
        tasksTwo = ftestutil.createTasks(shotTwo, 5)

        timelogs = sequence.getTimelogs(includeChildren=True)
        assert_equal(len(timelogs), 0, '0 timelogs were found')

        ftrack.createTimelog(
            start=datetime.datetime.now(),
            duration=1,
            contextId=shotOne
        )
        timelogs = sequence.getTimelogs(includeChildren=True)
        assert_equal(len(timelogs), 1, '1 timelogs were found')

        for index, task in enumerate(tasksOne):
            ftrack.createTimelog(
                start=datetime.datetime.now() + datetime.timedelta(days=index),
                duration=index,
                contextId=task
            )

        timelogs = sequence.getTimelogs(includeChildren=True)
        assert_equal(len(timelogs), 6, '6 timelogs were found')

        timelogs = shotOne.getTimelogs(includeChildren=True)
        assert_equal(len(timelogs), 6, '6 timelogs were found')

        timelogs = shotTwo.getTimelogs(includeChildren=True)
        assert_equal(len(timelogs), 0, '0 timelogs were found')

        ftrack.createTimelog(
            start=datetime.datetime.now(),
            duration=2,
            contextId=shotTwo
        )
        for index, task in enumerate(tasksTwo):
            ftrack.createTimelog(
                start=datetime.datetime.now() + datetime.timedelta(days=index),
                duration=index,
                contextId=task
            )

        timelogs = shotTwo.getTimelogs(includeChildren=True)
        assert_equal(len(timelogs), 6, '6 timelogs were found')

        timelogs = sequence.getTimelogs(includeChildren=True)
        assert_equal(len(timelogs), 12, '12 timelogs were found')
