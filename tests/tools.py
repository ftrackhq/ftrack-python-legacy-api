'''Helper tools for testing.'''

import re
import sys
import logging
from contextlib import contextmanager
from StringIO import StringIO

from nose.tools import *

# Now add in any missing implementations

try:
    assert_raises(Exception)
    
except TypeError:

    class _AssertRaisesContext(object):
        '''Context manager used by assert_raises.'''
    
        def __init__(self, expected, expected_regexp=None):
            self.expected = expected
            self.expected_regexp = expected_regexp
    
        def __enter__(self):
            return self
    
        def __exit__(self, exc_type, exc_value, tb):
            if exc_type is None:
                try:
                    exc_name = self.expected.__name__
                    
                except AttributeError:
                    exc_name = str(self.expected)
                
                raise AssertionError('{0} not raised'.format(exc_name))
            
            if not issubclass(exc_type, self.expected):
                # let unexpected exceptions pass through
                return False
            
            self.exception = exc_value # store for later retrieval
            if self.expected_regexp is None:
                return True
    
            expected_regexp = self.expected_regexp
            if isinstance(expected_regexp, basestring):
                expected_regexp = re.compile(expected_regexp)
            
            if not expected_regexp.search(str(exc_value)):
                raise AssertionError(
                    '"{0}" does not match "{1}"'
                    .format(expected_regexp.pattern, str(exc_value))
                )
            
            return True


    def assert_raises(exception, callable_obj=None, *args, **kwargs):
        '''Assert that *exception* is raised.
        
        Use as a context manager::
        
            with assert_raises(SomeException):
                do_something()
        
        .. note::
        
            The context manager stores the exception for further testing if
            required::
            
            with assert_raises(SomeException) as context:
                do_something()
                
            assert_equal(context.exception.code, 42)
        
            
        '''
        context = _AssertRaisesContext(exception)
        
        if callable_obj is None:
            return context
        
        with context:
            callable_obj(*args, **kwargs)


if not 'assert_raises_regexp' in vars():
    
    def assert_raises_regexp(exception, regexp, callable_obj=None,
                             *args, **kwargs):
        '''Assert that *exception* is raised and message matches *regexp*.
        
        Use as a context manager::
        
            with assert_raises(SomeException, 'Message pattern'):
                do_something()
        
        .. note::
        
            The context manager stores the exception for further testing if
            required::
            
            with assert_raises(SomeException) as context:
                do_something()
                
            assert_equal(context.exception.code, 42)
        
        '''
        context = _AssertRaisesContext(exception, regexp)
        
        if callable_obj is None:
            return context
        
        with context:
            callable_obj(*args, **kwargs)


@contextmanager
def capture_output():
    '''Capture output for duration of context.

    Example::

        with capture_output() as (output, error):
            foo()

        print output.getvalue()

    '''
    new_stdout, new_stderr = StringIO(), StringIO()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_stdout, new_stderr
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr


class CaptureLoggingHandler(logging.Handler):
    '''Capture logs.'''

    def __init__(self, *args, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs)
        self.records = []

    def emit(self, record):
        self.records.append(record)

    def clear(self):
        '''Clear captured records.'''
        del self.records[:]


@contextmanager
def capture_logging():
    '''Capture logging for duration of context.

    Example::

        with capture_logging() as records:
            foo()

        print records[0].getMessage()

    '''
    try:
        handler = CaptureLoggingHandler()
        logging.getLogger().addHandler(handler)
        yield handler.records
    finally:
        logging.getLogger().removeHandler(handler)
