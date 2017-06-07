# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import os
import datetime
import functools
import inspect
import random
import sys

import ftrack

from .tools import assert_raises_regexp

ALL_PERMISSIONS_API_KEY = '7545384e-a653-11e1-a82c-f23c91df25eb'
DENIED_CREATE_PERMISSIONS_API_KEY = '4485e361-cc4d-11e3-a534-20c9d0831e59'
DENIED_DELETE_PERMISSIONS_API_KEY = 'fb7da46e-cbce-11e3-902a-20c9d0831e59'
DENIED_READ_PERMISSIONS_API_KEY = '62a1a58c-cbb9-11e3-acd7-20c9d0831e59'
DENIED_WRITE_PERMISSIONS_API_KEY = 'e9a11fde-cc4a-11e3-b7f8-20c9d0831e59'
DENIED_MOVE_PERMISSIONS_API_KEY = '661ae4d7-da77-11e3-9778-20c9d0831e59'


class ApiKey():
    '''Context manager for altering API key temporarily.'''

    def __init__(self, apiKey):
        '''Instantiate with *apiKey* to set for duration of context.'''
        self._originalApiKey = os.environ['FTRACK_APIKEY']
        self.apiKey = apiKey

    def __enter__(self):
        '''Set API key to configured value..'''
        os.environ['FTRACK_APIKEY'] = self.apiKey

    def __exit__(self, type, value, traceback):
        '''Reset original API key value.'''
        os.environ['FTRACK_APIKEY'] = self._originalApiKey


def createPhase(user=None):
    '''Return a new phase and assign *user* if it is not None.'''
    show = ftrack.getShow(['test'])

    startdate = datetime.datetime.now()
    enddate = startdate + datetime.timedelta(days=7)

    phase = show.createPhase('Test phase', startdate, enddate)

    if user:
        phase.assignUser(user)

    return phase


def createBooking():
    '''Return a new booking.'''
    user = ftrack.getUsers().pop()

    startdate = datetime.datetime.now()
    enddate = startdate + datetime.timedelta(days=7)

    return user.createBooking('Test booking', startdate, enddate)


class BasePermissionTest(object):
    '''Set the API keys.'''
    _originalApiKey = os.environ.get('FTRACK_APIKEY', '')

    # If api key is set it will be used while running the tests.
    apiKey = None

    # Set list of api keys that should cause permission denied errors for this
    # test.
    permissionDeniedKeys = None

    @classmethod
    def setUpClass(cls):
        '''Perform per test class setup.'''
        if cls.apiKey:
            os.environ['FTRACK_APIKEY'] = cls.apiKey

    @classmethod
    def tearDownClass(cls):
        '''Perform per test class teardown.'''
        os.environ['FTRACK_APIKEY'] = cls._originalApiKey


class CreationPermissionTest(BasePermissionTest):
    '''Test creation permissions.'''

    permissionDeniedKeys = (DENIED_CREATE_PERMISSIONS_API_KEY,)

    def testCreateProject(self):
        '''Create a project.'''
        # Create show.
        showFullname = ftrack.getUUID()
        showName = ftrack.getUUID()
        workflows = ftrack.getProjectSchemes()

        ftrack.createShow(showFullname, showName, workflows[0])

    def testCreateObject(self):
        '''Create Shot, Task.'''
        show = ftrack.getShow(['test'])

        # Create shot.
        shotName = ftrack.getUUID()
        show.createShot(shotName)

        # Create task.
        taskType = show.getTaskTypes()[0]
        taskStatus = show.getTaskStatuses()[0]
        taskName = ftrack.getUUID()

        shot = ftrack.getShot(['test', 'python_api', 'shot1'])
        shot.createTask(taskName, taskType, taskStatus)

    def testCreateList(self):
        '''Create a Lists with Shot or AssetVersion type.'''
        show = ftrack.getShow(['test'])
        categories = ftrack.getListCategories()

        show.createList(ftrack.getUUID(), categories[0], ftrack.Shot)

        show.createList(
            ftrack.getUUID(),
            categories[0],
            ftrack.AssetVersion
        )

    def testCreatePhase(self):
        '''Create a Phase.'''
        createPhase()

    def testCreateBooking(self):
        '''Create a booking.'''
        createBooking()


class DeletionPermissionTest(BasePermissionTest):
    '''Test deletion permissions.'''

    permissionDeniedKeys = (DENIED_DELETE_PERMISSIONS_API_KEY,)

    def testDeleteObjects(self):
        '''Delete Task, Shot and Sequence.'''
        show = ftrack.getShow(['test'])

        # Create sequence
        sequenceName = ftrack.getUUID()
        sequence = show.createSequence(sequenceName)

        # Create shot
        shotName = ftrack.getUUID()
        shot = sequence.createShot(shotName)

        # Create task
        taskType = show.getTaskTypes()[0]
        taskStatus = show.getTaskStatuses()[0]
        taskName = ftrack.getUUID()
        task = shot.createTask(taskName, taskType, taskStatus)

        task.delete()

        shot.delete()

        sequence.delete()

    def testDeleteShow(self):
        '''Delete Show.'''

        # Create show
        showFullname = ftrack.getUUID()
        shoWname = ftrack.getUUID()
        workflows = ftrack.getProjectSchemes()
        show = ftrack.createShow(showFullname, shoWname, workflows[0])

        show.delete()

    def testRemoveObjectFromList(self):
        '''Remove item from shot and version Lists.'''
        show = ftrack.getShow(['test'])
        categories = ftrack.getListCategories()

        shotList = show.createList(
            ftrack.getUUID(),
            categories[0],
            ftrack.Shot
        )
        versionList = show.createList(
            ftrack.getUUID(),
            categories[0],
            ftrack.AssetVersion
        )

        shot1 = ftrack.getShot(['test', 'python_api', 'shot1'])

        shotList.append(shot1)

        shotList.remove(shot1)

        version = shot1.getAssets()[0].getVersions()[0]

        versionList.append(version)

        versionList.remove(version)

    def testDeleteVersion(self):
        '''Delete a version.'''
        myShot = ftrack.getShotFromPath('test.python_api.shot1')
        myTask = myShot.getTasks()[0]
        assetName = ftrack.getUUID()
        asset = myShot.createAsset(
            name=assetName,
            assetType='dai',
            task=myTask
        )
        version = asset.createVersion(taskid=myTask.getId())
        asset.publish()

        version.delete()
        asset.delete()

    def testDeletePhase(self):
        '''Delete a phase.'''
        with ApiKey(ALL_PERMISSIONS_API_KEY):
            phase = createPhase()

        phase.delete()

    def testDeleteBooking(self):
        '''Delete a booking.'''
        with ApiKey(ALL_PERMISSIONS_API_KEY):
            booking = createBooking()

        booking.delete()


class ReadingPermissionTest(BasePermissionTest):
    '''Test reading permissions.'''

    permissionDeniedKeys = (DENIED_READ_PERMISSIONS_API_KEY,)

    def testGetBuiltinAttribute(self):
        '''Get bid from a task.'''
        testTask = ftrack.getShot('test.fog.s1').getTasks()[0]
        testTask.get('bid')

    def testGetCustomAttribute(self):
        '''Get custom attribute.'''
        testTask = ftrack.getShot('test.fog.s1').getTasks()[0]
        testTask.get('test_number')


class WritingPermissionsTest(BasePermissionTest):
    '''Test writing permissions.'''

    permissionDeniedKeys = (DENIED_WRITE_PERMISSIONS_API_KEY,)

    def testSetBuiltinAttribute(self):
        '''Set bid for a task.'''
        testTask = ftrack.getShot('test.fog.s1').getTasks()[0]

        testTask.set('bid', 4.0)

    def testSetCustomAttribute(self):
        '''Set custom attribute for a task.'''
        testTask = ftrack.getShot('test.fog.s1').getTasks()[0]

        testTask.set(
            'test_number', random.randint(0, sys.maxint)
        )

    def testSetPhaseAttribute(self):
        '''Set data on a phase.'''
        with ApiKey(ALL_PERMISSIONS_API_KEY):
            phase = createPhase()

        phase.set('startdate', datetime.datetime.now())

    def testAssignUserToPhase(self):
        '''Assign a user to a phase.'''
        users = ftrack.getUsers()

        with ApiKey(ALL_PERMISSIONS_API_KEY):
            phase = createPhase()

        phase.assignUser(users[0])

    def testUnAssignUserToPhase(self):
        '''Un-assign a user from a phase.'''
        users = ftrack.getUsers()

        with ApiKey(ALL_PERMISSIONS_API_KEY):
            phase = createPhase(users[0])

        phase.unAssignUser(users[0])

    def testSetBookingAttribute(self):
        '''Set data on a booking.'''
        with ApiKey(ALL_PERMISSIONS_API_KEY):
            booking = createBooking()

        booking.set('startdate', datetime.datetime.now())


class MovePermissionsTest(BasePermissionTest):
    '''Test move permissions.'''

    permissionDeniedKeys = (DENIED_MOVE_PERMISSIONS_API_KEY,)

    def testChangeParentOfTask(self):
        '''Change parent of a task.'''
        project = ftrack.getProject('test')
        oldParent = ftrack.getShot('test.python_api.shot1')
        newParent = ftrack.getShot('test.python_api.shot2')

        taskType = project.getTaskTypes()[0]
        taskStatus = project.getTaskStatuses()[0]
        taskName = ftrack.getUUID()
        testTask = oldParent.createTask(taskName, taskType, taskStatus)

        testTask.set('parent_id', newParent.getId())


class PermissionTestFactory(object):

    @classmethod
    def _wrapMethod(cls, method, errorExpression):
        '''Build and return wrapper for *method*.

        See PermissionTestFactory for details.

        '''

        def wrapper(*args, **kw):
            # NOTE: In future could change this to explicitly
            # check for ftrack.PermissionDeniedError, but at the
            # moment some actions, such as deleting, still raise
            # FTrackError.
            with assert_raises_regexp(
                ftrack.FTrackError, errorExpression
            ):
                method(*args, **kw)

        functools.update_wrapper(wrapper, method)
        wrapper.__doc__ = 'Fail to {0}'.format(
            wrapper.__doc__[0].lower() + wrapper.__doc__[1:]
        )

        return wrapper

    @classmethod
    def construct(cls, name, baseTestClass, apiKey,
                  errorExpression='Permission denied.*'):
        '''Construct permission test with *name*, *baseTestClass* and *apiKey*.

        Return class with *baseTestClass* as a base and methods updated to
        reflect expected result based on *apiKey* and
        *baseTestClass.permissionDeniedKeys*.

        If the *apiKey* is one of the *baseTestClass* permissionDeniedKeys, then
        update methods to test expected failure due to an exception being
        raised which matches *errorExpression*.

        '''
        newClass = type(name, (baseTestClass,), {'apiKey': apiKey})

        permissionDeniedKeys = baseTestClass.permissionDeniedKeys
        if permissionDeniedKeys is None:
            permissionDeniedKeys = tuple()

        if apiKey in permissionDeniedKeys:
            for name, method in inspect.getmembers(
                baseTestClass, inspect.ismethod
            ):
                if name.startswith('test'):
                    wrapper = cls._wrapMethod(method, errorExpression)
                    setattr(newClass, name, wrapper)

        return newClass


# Create actual tests using factory.
TestCreationWithSufficientPermissions = PermissionTestFactory.construct(
    'TestCreationWithSufficientPermissions',
    CreationPermissionTest,
    ALL_PERMISSIONS_API_KEY
)


TestCreationWithoutSufficientPermissions = PermissionTestFactory.construct(
    'TestCreationWithoutSufficientPermissions',
    CreationPermissionTest,
    DENIED_CREATE_PERMISSIONS_API_KEY
)


TestDeletionWithSufficientPermissions = PermissionTestFactory.construct(
    'TestDeletionWithSufficientPermissions',
    DeletionPermissionTest,
    ALL_PERMISSIONS_API_KEY
)


TestDeletionWithoutSufficientPermissions = PermissionTestFactory.construct(
    'TestDeletionWithoutSufficientPermissions',
    DeletionPermissionTest,
    DENIED_DELETE_PERMISSIONS_API_KEY
)


TestReadingWithSufficientPermissions = PermissionTestFactory.construct(
    'TestReadingWithSufficientPermissions',
    ReadingPermissionTest,
    ALL_PERMISSIONS_API_KEY
)


TestReadingWithoutSufficientPermissions = PermissionTestFactory.construct(
    'TestReadingWithoutSufficientPermissions',
    ReadingPermissionTest,
    DENIED_READ_PERMISSIONS_API_KEY,
    # If permission is not granted for read, the attribute simply doesn't exist
    # client side. TODO: If this behaviour changes in future, update this test.
    errorExpression='Value .+ not found on this object'
)


TestWritingWithSufficientPermissions = PermissionTestFactory.construct(
    'TestWritingWithSufficientPermissions',
    WritingPermissionsTest,
    ALL_PERMISSIONS_API_KEY
)


TestWritingWithoutSufficientPermissions = PermissionTestFactory.construct(
    'TestWritingWithoutSufficientPermissions',
    WritingPermissionsTest,
    DENIED_WRITE_PERMISSIONS_API_KEY
)

TestMoveWithSufficientPermissions = PermissionTestFactory.construct(
    'TestMoveWithSufficientPermissions',
    MovePermissionsTest,
    ALL_PERMISSIONS_API_KEY
)


TestMoveWithoutSufficientPermissions = PermissionTestFactory.construct(
    'TestMoveWithoutSufficientPermissions',
    MovePermissionsTest,
    DENIED_MOVE_PERMISSIONS_API_KEY
)
