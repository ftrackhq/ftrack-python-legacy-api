# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

'''Tests for the restrict_timelogging_to_assigned setting.

These assertions should pass when the setting is active.
'''

import datetime
import uuid
import getpass

import ftrack


# FAIL: No context
createSuccess = False
try:
    ftrack.createTimelog(
        name='Arbitrary',
        start=datetime.datetime.now(),
        duration=4 * 60 * 60
    )
    createSuccess = True
except ftrack.FTrackError as error:
    print 'Error', error

assert createSuccess == False

# Create context
project = ftrack.getProjects()[0]
task = project.createTask('timelog-apitest-' + uuid.uuid1().hex)

# FAIL: New task
try:
    ftrack.createTimelog(
        start=datetime.datetime.now(),
        duration=4 * 60 * 60,
        contextId=task.getId()
    )
except ftrack.FTrackError as error:
    print 'Error', error

assert len(task.getTimelogs()) == 0

# PASS: Open task
task.set('isopen', True)
try:
    ftrack.createTimelog(
        start=datetime.datetime.now(),
        duration=4 * 60 * 60,
        contextId=task.getId()
    )
except ftrack.FTrackError as error:
    print 'Error', error

assert len(task.getTimelogs()) == 1
task.set('isopen', False)

# PASS: Assigned task
currentUser = ftrack.User(getpass.getuser())
task.assignUser(currentUser)
try:
    ftrack.createTimelog(
        start=datetime.datetime.now(),
        duration=4 * 60 * 60,
        contextId=task.getId()
    )
except ftrack.FTrackError as error:
    print 'Error', error

assert len(task.getTimelogs()) == 2

print 'Passed all tests!'
