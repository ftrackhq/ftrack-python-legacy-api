# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack

import ftrack

import ftestutil
from .tools import ok_, assert_equal, assert_raises


class TestManagers():
    '''Test create and get managers.'''

    def setUp(self):
        '''Perform per test setup.'''
        self.project = ftestutil.createProject()

    def tearDown(self):
        '''Perform per test teardown.'''
        self.project.delete()

    def testGetManagerTypes(self):
        '''Get manager types.'''
        managerTypes = ftrack.getManagerTypes()
        ok_(len(managerTypes) > 0, 'No manager types found.')

        managerName = managerTypes[0].getName()
        managerType = ftrack.ManagerType(managerName)

        assert_equal(
            managerTypes[0].getId(),
            managerType.getId(),
            'It is not the expected manager type.'
        )

    def testCreateAndGetManagerFromProject(self):
        '''Create managers and get them from a project.'''
        managerType = ftrack.getManagerTypes()[0]
        user = ftrack.User('jenkins')
        manager = self.project.createManager(user, managerType)

        assert_equal(
            manager.getUser().getId(),
            user.getId(),
            'User id is not correct.'
        )

        assert_equal(
            manager.getType().getId(),
            managerType.getId(),
            'Type id is not correct.'
        )

        managers = self.project.getManagers()
        assert_equal(
            len(managers),
            1,
            'There is not 1 manager.'
        )

        assert_equal(
            managers[0].getId(),
            manager.getId(),
            'It is not the expected manager.'
        )

    def testCreateAndGetManagerFromShot(self):
        '''Create managers and get them from a shot.'''
        shot = self.project.createShot('010')
        managerType = ftrack.getManagerTypes()[0]
        user = ftrack.User('jenkins')
        manager = shot.createManager(user, managerType)

        assert_equal(
            manager.getUser().getId(),
            user.getId(),
            'User id is not correct.'
        )

        assert_equal(
            manager.getType().getId(),
            managerType.getId(),
            'Type id is not correct.'
        )

        managers = shot.getManagers()
        assert_equal(
            len(managers),
            1,
            'There is not 1 manager.'
        )

        assert_equal(
            managers[0].getId(),
            manager.getId(),
            'It is not the expected manager.'
        )

    def testCreateAndGetManagerFromProjectAndShot(self):
        '''Create managers and get them from a project and shot.'''
        shot = self.project.createShot('010')
        managerType = ftrack.getManagerTypes()[0]

        # Use two different users since getManagers will only return the highest
        # manager per user for an entity.
        user1 = ftrack.User('jenkins')
        user2 = ftrack.User('standard')
        self.project.createManager(user1, managerType)
        shot.createManager(user2, managerType)

        shotManagers = shot.getManagers()
        print shotManagers
        assert_equal(
            len(shotManagers),
            2,
            'There is not 2 manager.'
        )

        projectManagers = self.project.getManagers()
        assert_equal(
            len(projectManagers),
            1,
            'There is not 1 manager.'
        )

    def testRemoveManager(self):
        '''Remove an existing manager.'''
        managerType = ftrack.getManagerTypes()[0]
        user = ftrack.User('jenkins')
        manager = self.project.createManager(user, managerType)

        managers = self.project.getManagers()
        assert_equal(
            len(managers),
            1,
            'There is not 1 manager.'
        )

        manager.delete()

        managers = self.project.getManagers()
        assert_equal(
            len(managers),
            0,
            'There is not 0 manager.'
        )

    def testRemoveManagerTypeWithManagers(self):
        '''Remove an existing manager type that has managers.'''
        managerType = ftrack.getManagerTypes()[0]
        user = ftrack.User('jenkins')
        self.project.createManager(user, managerType)

        with assert_raises(ftrack.FTrackError):
            managerType.delete()
