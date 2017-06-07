# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import ftrack

from .tools import ok_, assert_equal, assert_raises


class MockClass(object):
    '''Mock class for testing.'''

    def method(self, key):
        '''Mock method for testing.'''


def mockFunction(mutable, x, y=2):
    '''Mock function for testing.'''
    mutable['called'] = True
    return x + y


def returnMutable():
    '''Return mutable value.'''
    return {'key': 'value'}


class CacheInterfaceTest(object):
    '''Test cache conforms to interface.'''

    def setUp(self):
        '''Perform per test setup.'''
        self.cache = self.getCache()

    def tearDown(self):
        '''Perform per test teardown.'''
        self.cache.clear()

    def getCache(self):
        '''Return cache instance to test against.'''
        raise NotImplementedError()

    def testGetValidKey(self):
        '''Retrieve value for valid key.'''
        self.cache.set('key', 'value')
        assert_equal(self.cache.get('key'), 'value')

    def testGetInvalidKey(self):
        '''Fail to retrieve value for invalid key.'''
        with assert_raises(KeyError):
            self.cache.get('key')

    def testSet(self):
        '''Set value for key.'''
        self.cache.set('key', 'value')
        assert_equal(self.cache.get('key'), 'value')

        self.cache.set('key', 'newValue')
        assert_equal(self.cache.get('key'), 'newValue')

    def testRemoveValidKey(self):
        '''Remove entry for valid key.'''
        self.cache.set('key', 'value')
        assert_equal(self.cache.get('key'), 'value')

        self.cache.remove('key')

        with assert_raises(KeyError):
            self.cache.get('key')

    def testRemoveInvalidKey(self):
        '''Fail to remove entry for invalid key.'''
        with assert_raises(KeyError):
            self.cache.remove('key')

    def testKeys(self):
        '''Retrieve list of current keys.'''
        assert_equal(self.cache.keys(), [])

        self.cache.set('keyA', 'value')
        self.cache.set('keyB', 'value')
        assert_equal(
            sorted(self.cache.keys()),
            sorted(['keyA', 'keyB'])
        )

        self.cache.remove('keyA')
        assert_equal(self.cache.keys(), ['keyB'])

    def testClear(self):
        '''Remove all keys.'''
        assert_equal(len(self.cache.keys()), 0)

        self.cache.set('keyA', 'value')
        self.cache.set('keyB', 'value')
        assert_equal(len(self.cache.keys()), 2)

        self.cache.clear()
        assert_equal(len(self.cache.keys()), 0)

    def testClearWithPattern(self):
        '''Remove all keys matching pattern.'''
        assert_equal(len(self.cache.keys()), 0)

        self.cache.set('keyA', 'value')
        self.cache.set('keyB', 'value')
        self.cache.set('key1', 'value')
        self.cache.set('key2', 'value')

        assert_equal(len(self.cache.keys()), 4)

        self.cache.clear(pattern='^key\d+')
        assert_equal(len(self.cache.keys()), 2)

        assert_equal(set(self.cache.keys()), set(['keyA', 'keyB']))

        self.cache.clear(pattern='key')
        assert_equal(len(self.cache.keys()), 0)


class TestMemoryCache(CacheInterfaceTest):
    '''Test MemoryCache.'''

    def getCache(self):
        '''Return cache instance to test against.'''
        return ftrack.cache.MemoryCache()


class TestKeyMaker(object):
    '''Test KeyMaker.'''

    def __init__(self):
        '''Initialise test.'''
        self.keyMaker = ftrack.cache.KeyMaker()

    def testKey(self):
        '''Generate key for objects.'''
        def _assertKey(obj, expected):
            '''Assert that generated key for *obj* matches *expected*.'''
            assert_equal(
                self.keyMaker.key(obj),
                expected
            )

        for obj, expected in [
            (None, '\x80\x02N.'),
            ((), '\x03\x03'),
            ({'key': 'value'},
             '\x01\x80\x02U\x03keyq\x01.\x02\x80\x02U\x05valueq\x01.\x01'),
            (MockClass, '\x04MockClass\x00tests.test_cache'),
            (MockClass.method, '\x04method\x00MockClass\x00tests.test_cache'),
            (mockFunction, '\x04mockFunction\x00tests.test_cache'),
            (max, '\x04max')
        ]:
            _assertKey.description = 'Generate key for {0}'.format(obj)
            yield _assertKey, obj, expected


class TestMemoiser(object):
    '''Test Memoiser.'''

    def setUp(self):
        '''Perform per test setup.'''
        self.memoiser = ftrack.cache.Memoiser()

    def _assertCall(self, args=None, kw=None, expected=3, memoised=True):
        '''Assert call *memoised* for *args* and *kw* with *expected* result.'''
        mapping = {'called': False}
        if args is not None:
            args = (mapping,) + args
        else:
            args = (mapping,)

        result = self.memoiser.call(mockFunction, args, kw)

        assert_equal(result, expected)
        assert_equal(mapping['called'], not memoised)

    def testCall(self):
        '''Call function.'''
        # Initial call should not be memoised so function is executed.
        self._assertCall(args=(1,), memoised=False)

        # Identical call should be memoised so function is not executed again.
        self._assertCall(args=(1,), memoised=True)

        # Differing call is not memoised so function is executed.
        self._assertCall(args=(3,), expected=5, memoised=False)

    def testCallVariations(self):
        '''Call function with identical arguments using variable format.'''
        # Call function once to ensure is memoised.
        self._assertCall(args=(1,), memoised=False)

        # Each of the following calls should equate to the same key and make
        # use of the memoised value.
        self._assertCall(kw={'x': 1})
        self._assertCall(kw={'x': 1, 'y': 2})
        self._assertCall(args=(1, ), kw={'y': 2})
        self._assertCall(args=(1, ))

        # The following calls should all be treated as new variations and so
        # not use any memoised value.
        self._assertCall(kw={'x': 2}, expected=4, memoised=False)
        self._assertCall(kw={'x': 3, 'y': 2}, expected=5, memoised=False)
        self._assertCall(args=(4, ), kw={'y': 2}, expected=6, memoised=False)
        self._assertCall(args=(5, ), expected=7, memoised=False)

    def testMutableReturnValue(self):
        '''Avoid side effects for returned mutable arguments.'''
        resultA = self.memoiser.call(returnMutable)
        assert_equal(resultA, {'key': 'value'})

        # Modify mutable externally and check that stored memoised value is
        # unchanged.
        del resultA['key']

        resultB = self.memoiser.call(returnMutable)
        assert_equal(resultB, {'key': 'value'})


class TestMemoiserDecorator(object):
    '''Test memoise decorator.'''

    def _assertCall(self, args=None, kw=None, expected=3, memoised=True):
        '''Assert call *memoised* for *args* and *kw* with *expected* result.'''
        if args is None:
            args = ()
        if kw is None:
            kw = {}

        mapping = {'called': False}
        result = self.decorated(mapping, *args, **kw)

        assert_equal(result, expected)
        assert_equal(mapping['called'], not memoised)

    @ftrack.cache.memoiseDecorator(ftrack.cache.Memoiser())
    def decorated(self, mutable, x, y=2):
        '''Memoised decorated method.'''
        mutable['called'] = True
        return x + y

    def testDecorator(self):
        '''Call memoised decorated function.'''
         # Initial call should not be memoised so function is executed.
        self._assertCall(args=(1,), memoised=False)

        # Identical call should be memoised so function is not executed again.
        self._assertCall(args=(1,), memoised=True)

        # Differing call is not memoised so function is executed.
        self._assertCall(args=(3,), expected=5, memoised=False)
