# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import ftrack

from tools import ok_


class TestGroups():
    '''Test groups.'''

    def testGetGroups(self):
        '''Get groups from ftrack.'''
        groupNames = [group.get('name') for group in ftrack.getGroups()]
        ok_('testgroup1' in groupNames, 'Test group exists.')
        ok_('subgroup1' not in groupNames, 'Subgroup not included.')

    def testGetSubgroup(self):
        '''Get subgroups.'''
        group = ftrack.Group('testgroup1')
        groupNames = [group.get('name') for group in group.getSubgroups()]

        ok_('subgroup1' in groupNames, 'Subgroup included.')
        ok_('subgroup2' in groupNames, 'Subgroup included.')
        ok_(len(groupNames) == 2, 'Two subgroups.')

    def testGetMembers(self):
        '''Get members.'''
        group = ftrack.Group('testgroup1')
        memberNames = [member.get('username') for member in group.getMembers()]

        ok_('jenkins' in memberNames, 'Member included.')
        ok_('standard' in memberNames, 'Member included.')
        ok_(len(memberNames) == 2, 'Two members.')
