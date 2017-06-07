# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack

import ftrack

import ftestutil
from tools import ok_, assert_equal


class TestRoles():
    '''Test create and get managers.'''

    def setUp(self):
        '''Perform per test setup.'''
        self.project = ftestutil.createProject()
        self.role = ftrack.Role('User')
        self.user = ftrack.User('jenkins')

    def tearDown(self):
        '''Perform per test teardown.'''
        self.project.delete()
        self.user.removeRole(self.role)

    def _getUserRoleIds(self, user):
        '''Return a list with role ids from *user*.'''
        ids = []
        for role in user.getRoles():
            ids.append(role.getId())

        return ids

    def testAddRemoveRoles(self):
        '''Add and remove roles to user.'''
        roleIds = self._getUserRoleIds(self.user)
        ok_(self.role.getId() not in roleIds, 'User should not have role.')

        self.user.addRole(self.role, self.project)

        roleIds = self._getUserRoleIds(self.user)
        ok_(self.role.getId() in roleIds, 'User should now have role.')

        projects = self.user.getRoleProjects(self.role)
        ok_(len(projects) == 1)
        ok_(projects[0].getId() == self.project.getId())

        self.user.removeRole(self.role)

        roleIds = self._getUserRoleIds(self.user)
        ok_(self.role.getId() not in roleIds, 'User should not have role.')

        self.user.addRole(self.role)
        projects = self.user.getRoleProjects(self.role)
        assert_equal(len(projects), len(ftrack.getProjects()))

        self.user.removeRole(self.role)

        roleIds = self._getUserRoleIds(self.user)
        ok_(self.role.getId() not in roleIds, 'User should not have role.')
