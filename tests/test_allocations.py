# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import ftrack

from tools import ok_


STANDARD_USER_ID = 'd18b2062-e7af-11e1-84a5-f23c91df25eb'
JENKINS_USER_ID = 'd07ae5d0-66e1-11e1-b5e9-f23c91df25eb'


class TestAllocations():
    '''Test allocations.'''

    def testGetAllocatedUsers(self):
        '''Get allocated users from project.'''
        project = ftrack.getProject('test')
        users = project.getAllocatedUsers()
        userIds = [user.getId() for user in users]

        ok_(STANDARD_USER_ID in userIds, 'User included.')
        ok_(JENKINS_USER_ID in userIds, 'User included.')
        ok_(len(userIds) == 2, 'Two users.')

    def testGetAllocatedGroups(self):
        '''Get allocated groups from project.'''
        project = ftrack.getProject('test')
        groups = project.getAllocatedGroups()
        groupNames = [group.get('name') for group in groups]

        ok_('subgroup1' in groupNames, 'Subgroup included.')
        ok_('testgroup1' in groupNames, 'group included.')
        ok_('projectgroup' in groupNames, 'project group included.')
        ok_(len(groupNames) == 3, 'Three groups.')
