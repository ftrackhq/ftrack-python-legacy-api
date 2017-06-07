# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack

from nose.tools import ok_, assert_equal
import ftrack
import uuid


class TestCustomAttributes:
    '''Class representing custom attribute tests.'''

    def _createTask(self):
        '''Create a new task and return it.'''
        show = ftrack.getShowFromPath('test')
        shotname = ftrack.getUUID()
        shot = ftrack.getSequenceFromPath(
            'test.python_api'
        ).createShot(
            shotname
        )

        taskType = show.getTaskTypes()[0]
        taskStatus = show.getTaskStatuses()[0]
        taskname = ftrack.getUUID()
        task = shot.createTask(taskname, taskType, taskStatus)

        return task

    def testAttributeTypes(self):
        '''Get values and verify that the types are correct.'''
        task = self._createTask()

        number = task.get('test_number')
        ok_(isinstance(number, float), 'Value returned is float')

        task.set('test_number', 3.56)
        number = task.get('test_number')
        ok_(isinstance(number, float), 'Value returned is float')
        ok_(number == 3.56, 'Value is correct')

        checkValue = task.get('test_check')
        ok_(
            isinstance(checkValue, bool),
            'Value returned is bool'
        )

        task.set('test_check', True)
        checkValue = task.get('test_check')
        ok_(isinstance(checkValue, bool), 'Value returned is bool')
        ok_(checkValue is True, 'Value is correct')

        task.set('test_check', False)
        checkValue = task.get('test_check')
        ok_(isinstance(checkValue, bool), 'Value returned is bool')
        ok_(checkValue is False, 'Value is correct')

    def test_3_multiple(self):
        task = self._createTask()

        task.set('test_check', True)
        task.set('test_number', 5.56)

        ok_(task.get('test_check') is True, 'Value is correct')
        ok_(task.get('test_number') == 5.56, 'Value is correct')

        task.set({
            'test_check': False,
            'test_number': 5.57
        })

        ok_(task.get('test_check') is False, 'Value is correct')
        ok_(task.get('test_number') == 5.57, 'Value is correct')

    def testText(self):
        '''Get and set text custom attribute.'''
        task = self._createTask()
        randomString1 = uuid.uuid1().hex
        randomString2 = uuid.uuid1().hex
        task.set('test_text', randomString1)
        assert_equal(
            task.get('test_text'),
            randomString1,
            'Strings are equal.'
        )
        task.set('test_text', randomString2)
        assert_equal(
            task.get('test_text'),
            randomString2,
            'Numbers are equal.'
        )

    def testNumber(self):
        '''Get and set number custom attribute.'''
        task = self._createTask()
        number1 = 345
        number2 = 456.345
        task.set('test_number', number1)
        assert_equal(
            task.get('test_number'),
            number1,
            'Strings are equal.'
        )
        task.set('test_number', number2)
        assert_equal(
            task.get('test_number'),
            number2,
            'Numbers are equal.'
        )
