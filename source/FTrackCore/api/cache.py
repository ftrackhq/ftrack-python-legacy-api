# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

'''Caching framework.

Defines a standardised :py:class:`Cache` interface for storing data against
specific keys. Key generation is also standardised using a :py:class:`KeyMaker`
interface.

Combining a Cache and KeyMaker allows for memoisation of function calls with
respect to the arguments used by using a :py:class:`Memoiser`.

As a convenience a simple :py:func:`memoise` decorator is included for quick
memoisation of function using a global cache and standard keymaker.

'''

import collections
import functools
import abc
import copy
import inspect
import re
try:
    import cPickle as pickle
except ImportError:  # pragma: no cover
    import pickle


class Cache(object):
    '''Cache interface.

    Derive from this to define concrete cache implementations. A cache is
    centered around the concept of key:value pairings where the key is unique
    across the cache.

    '''

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get(self, key):
        '''Return value for *key*.

        Raise :py:exc:`KeyError` if *key* not found.

        '''

    @abc.abstractmethod
    def set(self, key, value):
        '''Set *value* for *key*.'''

    @abc.abstractmethod
    def remove(self, key):
        '''Remove *key* and return stored value.

        Raise :py:exc:`KeyError` if *key* not found.

        '''

    @abc.abstractmethod
    def keys(self):
        '''Return list of keys at this current time.

        .. warning::

            Actual keys may differ from those returned due to timing of access.

        '''

    def clear(self, pattern=None):
        '''Remove all keys matching *pattern*.

        *pattern* should be a regular expression string.

        If *pattern* is None then all keys will be removed.

        '''
        if pattern is not None:
            pattern = re.compile(pattern)

        for key in self.keys():
            if pattern is not None:
                if not pattern.search(key):
                    continue

            try:
                self.remove(key)
            except KeyError:
                pass


class MemoryCache(Cache):
    '''Memory based cache.'''

    def __init__(self):
        '''Initialise cache.'''
        self._cache = {}
        super(MemoryCache, self).__init__()

    def get(self, key):
        '''Return value for *key*.

        Raise :py:exc:`KeyError` if *key* not found.

        '''
        return self._cache[key]

    def set(self, key, value):
        '''Set *value* for *key*.'''
        self._cache[key] = value

    def remove(self, key):
        '''Remove *key*.

        Raise :py:exc:`KeyError` if *key* not found.

        '''
        del self._cache[key]

    def keys(self):
        '''Return list of keys at this current time.

        .. warning::

            Actual keys may differ from those returned due to timing of access.

        '''
        return self._cache.keys()


class KeyMaker(object):
    '''Generate unique keys for objects.'''

    def __init__(self):
        '''Initialise key maker.'''
        super(KeyMaker, self).__init__()
        self.itemSeparator = '\0'
        self.mappingIdentifier = '\1'
        self.mappingPairSeparator = '\2'
        self.iterableIdentifier = '\3'
        self.nameIdentifier = '\4'

    def key(self, *objects):
        '''Return key for *objects*.

        Each object may be any Python object that is pickleable.

        '''
        # Iterate here to avoid manner in which objects passed in from
        # affecting the generated key. Without this, the key would also have
        # iterable identifiers surrounding it making partial key matches harder.
        keys = []
        for obj in objects:
            keys.append(self._key(obj))

        return self.itemSeparator.join(keys)

    def _key(self, obj):
        '''Return key for *obj*.

        Returned key will be a pickle like string representing the *obj*. This
        allows for typically non-hashable objects to be used in key generation
        (such as dictionaries).

        If *obj* is iterable then each item in it shall also be passed to this
        method to ensure correct key generation.

        Special markers are used to distinguish handling of specific cases in
        order to ensure uniqueness of key corresponds directly to *obj*.

        Example::

            >>> keyMaker = KeyMaker()
            >>> def add(x, y):
            ...     "Return sum of *x* and *y*."
            ...     return x + y
            ...
            >>> keyMaker.key(add, (1, 2))
            '\x04add\x00__main__\x00\x03\x80\x02K\x01.\x00\x80\x02K\x02.\x03'
            >>> keyMaker.key(add, (1, 3))
            '\x04add\x00__main__\x00\x03\x80\x02K\x01.\x00\x80\x02K\x03.\x03'

        '''
        # TODO: Consider using a more robust and comprehensive solution such as
        # dill (https://github.com/uqfoundation/dill).
        if isinstance(obj, collections.Iterable):
            if isinstance(obj, basestring):
                return pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)

            if isinstance(obj, collections.Mapping):
                contents = self.itemSeparator.join([
                    (
                        self._key(key) +
                        self.mappingPairSeparator +
                        self._key(value)
                    )
                    for key, value in sorted(obj.items())
                ])
                return (
                    self.mappingIdentifier +
                    contents +
                    self.mappingIdentifier
                )

            else:
                contents = self.itemSeparator.join([
                    self._key(item) for item in obj
                ])
                return (
                    self.iterableIdentifier +
                    contents +
                    self.iterableIdentifier
                )

        elif inspect.ismethod(obj):
            return ''.join((
                self.nameIdentifier,
                obj.__name__,
                self.itemSeparator,
                obj.im_class.__name__,
                self.itemSeparator,
                obj.__module__
            ))

        elif inspect.isfunction(obj) or inspect.isclass(obj):
            return ''.join((
                self.nameIdentifier,
                obj.__name__,
                self.itemSeparator,
                obj.__module__
            ))

        elif inspect.isbuiltin(obj):
            return self.nameIdentifier + obj.__name__

        else:
            return pickle.dumps(obj, pickle.HIGHEST_PROTOCOL)


class Memoiser(object):
    '''Memoise function calls using a :class:`KeyMaker` and :class:`Cache`.

    Example::

        >>> memoiser = Memoiser(MemoryCache(), KeyMaker())
        >>> def add(x, y):
        ...     "Return sum of *x* and *y*."
        ...     print 'Called'
        ...     return x + y
        ...
        >>> memoiser.call(add, (1, 2), {})
        Called
        >>> memoiser.call(add, (1, 2), {})
        >>> memoiser.call(add, (1, 3), {})
        Called

    '''

    def __init__(self, cache=None, keyMaker=None):
        '''Initialise with *cache* and *keyMaker* to use.

        If *cache* is not specified a default :py:class:`MemoryCache` will be
        used. Similarly, if *keyMaker* is not specified a default
        :py:class:`KeyMaker` will be used.

        '''
        self.cache = cache
        if self.cache is None:
            self.cache = MemoryCache()

        self.keyMaker = keyMaker
        if self.keyMaker is None:
            self.keyMaker = KeyMaker()

        super(Memoiser, self).__init__()

    def call(self, function, args=None, kw=None):
        '''Call *function* with *args* and *kw* and return result.

        If *function* was previously called with exactly the same arguments
        then return cached result if available.

        Store result for call in cache.

        '''
        if args is None:
            args = ()

        if kw is None:
            kw = {}

        # Support arguments being passed as positionals or keywords.
        arguments = inspect.getcallargs(function, *args, **kw)

        key = self.keyMaker.key(function, arguments)
        try:
            value = self.cache.get(key)

        except KeyError:
            value = function(*args, **kw)
            self.cache.set(key, value)

        # Return copy of value to avoid stored value being inadvertently
        # altered by the caller.
        return copy.deepcopy(value)


def memoiseDecorator(memoiser):
    '''Decorator to memoise function calls using *memoiser*.'''
    def outer(function):

        @functools.wraps(function)
        def inner(*args, **kw):
            return memoiser.call(function, args, kw)

        return inner

    return outer


#: Default memoiser.
memoiser = Memoiser()

#: Default memoise decorator using standard cache and keymaker.
memoise = memoiseDecorator(memoiser)
