
import os
import tempfile

import ftrack

from .tools import assert_equal, assert_raises_regexp


class Base(object):
    '''Test data.'''

    def setUp(self):
        '''Perform per test setup.
        
        Instantiate data instance as self.data and populate initially with
        self.initialContents.
        
        '''
        self.initialContents = 'test data'
        
    def tearDown(self):
        '''Perform per test teardown.'''
        del self.data
        
    def testRead(self):
        '''Return content from current position up to *limit*.'''
        assert_equal(self.data.read(5), self.initialContents[:5])
        assert_equal(self.data.read(), self.initialContents[5:])
        
    def testWrite(self):
        '''Write content at current position.'''
        assert_equal(self.data.read(), self.initialContents)
        self.data.write('more test data')
        self.data.seek(0)
        assert_equal(self.data.read(), self.initialContents + 'more test data')
        
    def testFlush(self):
        '''Flush buffers ensuring data written.'''
        # TODO: Implement better test than just calling function.
        self.data.flush()
        
    def testSeek(self):
        '''Move internal pointer to *position*.'''
        self.data.seek(5)
        assert_equal(self.data.read(), 'data')
        
    def testTell(self):
        '''Return current position of internal pointer.'''
        assert_equal(self.data.tell(), 0)
        self.data.seek(5)
        assert_equal(self.data.tell(), 5)
        
    def testClose(self):
        '''Flush buffers and prevent further access.'''
        self.data.close()
        with assert_raises_regexp(ValueError, 'I/O operation on closed file'):
            self.data.read()


class TestFileWrapper(Base):
    '''Test file wrapper data.'''
    
    def setUp(self):
        '''Perform per test setup.'''
        super(TestFileWrapper, self).setUp()
        fileDescriptor, path = tempfile.mkstemp()
        fileObject = os.fdopen(fileDescriptor, 'r+')
        fileObject.write(self.initialContents)
        fileObject.seek(0)
        self.data = ftrack.FileWrapper(fileObject)


class TestFile(Base):
    '''Test file data.'''
    
    def setUp(self):
        '''Perform per test setup.'''
        super(TestFile, self).setUp()
        fileDescriptor, path = tempfile.mkstemp()
        fileObject = os.fdopen(fileDescriptor, 'r+')
        fileObject.write(self.initialContents)
        fileObject.flush()
        fileObject.close()
        
        self.data = ftrack.File(path, 'r+')


class TestString(Base):
    '''Test string data.'''
    
    def setUp(self):
        '''Perform per test setup.'''
        super(TestString, self).setUp()
        self.data = ftrack.String(self.initialContents)
