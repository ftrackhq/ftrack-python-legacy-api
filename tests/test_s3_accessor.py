# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack

from uuid import uuid4 as uuid

import ftrack

from .tools import assert_equal, assert_raises, assert_raises_regexp


class TestS3Accessor(object):
    '''Test S3 accessor.'''

    def __init__(self, *args, **kw):
        '''Initialise test.'''
        self.prefix = ('01e07b30-d405-11e2-8b8b-0800200c9a66/{0}'
                       .format(uuid().hex))
        super(TestS3Accessor, self).__init__(*args, **kw)
        
    def setUp(self):
        '''Perform per test setup.'''
        self.accessor = ftrack.S3Accessor(
            'ftrack-locations',
            'AKIAJVUT7Z2IJTXJB25Q',
            'uCOifS/cJSRqbN8t/umElEnAr8uD7s+tUiRlVGc3'
        )
        
        # Ensure clean state prior to test start
        self.cleanup()
        
    def tearDown(self):
        '''Perform per test teardown.'''
        self.cleanup()
        
    def cleanup(self):
        '''Cleanup storage.'''
        # Ensure clean state
        prefix = self.prefix + '/'
        root = self.prefix.split('/', 1)[0] + '/'
        
        for key in self.accessor.bucket.list(prefix=prefix):
            if root.startswith(key.name):
                # Don't delete root test directory.
                continue
            
            self.accessor.bucket.delete_key(key.name)
    
    def randomDirectoryPath(self):
        '''Return a random directory path under self.prefix.'''
        return '/'.join((self.prefix, uuid().hex))
    
    def randomFilePath(self, directoryPath=None):
        '''Return a random file path under *directoryPath*.
        
        If *directoryPath* not specified will generate one using
        randomDirectoryPath.
        
        '''
        if directoryPath is None:
            directoryPath = self.randomDirectoryPath()
        
        return '/'.join((directoryPath, '{0}.txt'.format(uuid().hex)))
        
    def testGetFilesystemPath(self):
        '''Convert path to filesystem path unsupported.'''
        with assert_raises(ftrack.AccessorUnsupportedOperationError):
            self.accessor.getFilesystemPath('a/path')
    
    def testList(self):
        '''List entries.'''
        assert_equal(len(self.accessor.list(self.prefix)), 0)
        
        path = self.randomDirectoryPath()
        self.accessor.makeContainer(path)
        
        listing = self.accessor.list(self.prefix)
        assert_equal(len(listing), 1)

        # Returned item is a valid resource
        assert_equal(self.accessor.exists(listing[0]), True)
        
    def testExists(self):
        '''Check whether path exists.'''
        assert_equal(self.accessor.exists(''), True)
        assert_equal(self.accessor.exists(self.prefix + '/missing'), False)
        
        directoryPath = self.randomDirectoryPath()
        assert_equal(self.accessor.exists(directoryPath), False)
        self.accessor.makeContainer(directoryPath)
        assert_equal(self.accessor.exists(directoryPath), True)
        
        filePath = self.randomFilePath(directoryPath)
        assert_equal(self.accessor.exists(filePath), False)
        data = self.accessor.open(filePath, 'w+')
        data.write('test data.')
        data.close()
        assert_equal(self.accessor.exists(filePath), True)
        
    def testIsFile(self):
        '''Check whether path is a file.'''
        directoryPath = self.randomDirectoryPath()
        self.accessor.makeContainer(directoryPath)
        assert_equal(self.accessor.isFile(directoryPath), False)
        
        filePath = self.randomFilePath(directoryPath)
        assert_equal(self.accessor.isFile(filePath), False)
        data = self.accessor.open(filePath, 'w+')
        data.write('test data.')
        data.close()
        assert_equal(self.accessor.isFile(filePath), True)
        
    def testIsContainer(self):
        '''Check whether path is a container.'''
        directoryPath = self.randomDirectoryPath()
        assert_equal(self.accessor.isContainer(directoryPath), False)
        self.accessor.makeContainer(directoryPath)
        assert_equal(self.accessor.isContainer(directoryPath), True)
        
        filePath = self.randomFilePath(directoryPath)
        data = self.accessor.open(filePath, 'w+')
        data.write('test data.')
        data.close()
        assert_equal(self.accessor.isContainer(filePath), False)
        
    def testIsSequence(self):
        '''Check whether path is a sequence.'''
        with assert_raises(ftrack.AccessorUnsupportedOperationError):
            self.accessor.isSequence('foo.%04d.exr')
        
    def testOpen(self):
        '''Open file.'''
        directoryPath = self.randomDirectoryPath()
        self.accessor.makeContainer(directoryPath)
        
        with assert_raises_regexp(ftrack.AccessorResourceInvalidError,
                                  'Cannot open a directory'):
            self.accessor.open(directoryPath, 'r')
        
        filePath = self.randomFilePath(directoryPath)
        
        with assert_raises(ftrack.AccessorResourceNotFoundError):
            self.accessor.open(filePath, 'r')
        
        data = self.accessor.open(filePath, 'w+')
        assert_equal(isinstance(data, ftrack.Data), True)
        assert_equal(data.read(), '')

        data.write('test data')
        data.close()
                
        data = self.accessor.open(filePath, 'r')
        assert_equal(data.read(), 'test data')
        data.close()
        
    def testRemove(self):
        '''Delete path.'''
        directoryPath = self.randomDirectoryPath()
        filePath = self.randomFilePath(directoryPath)
        self.accessor.makeContainer(directoryPath)
        data = self.accessor.open(filePath, 'w+')
        data.write('test data.')
        data.close()
        
        # Non-empty container
        with assert_raises(ftrack.AccessorContainerNotEmptyError):
            self.accessor.remove(directoryPath)
            
        # File
        self.accessor.remove(filePath)
        
        # Empty directory
        self.accessor.remove(directoryPath)
        
    def testMakeContainer(self):
        '''Create container.'''
        path = self.randomDirectoryPath()
        assert_equal(self.accessor.exists(path), False)
        self.accessor.makeContainer(path)
        assert_equal(self.accessor.exists(path), True)
        assert_equal(self.accessor.isContainer(path), True)
        assert_equal(self.accessor.isFile(path), False)
        
        # Existing succeeds
        self.accessor.makeContainer(path)
        
        # Non-recursive fails
        path += '/a/b/c'
        with assert_raises(ftrack.AccessorParentResourceNotFoundError):
            self.accessor.makeContainer(path, recursive=False)

    def testGetContainer(self):
        '''Get container from resourceIdentifier.'''        
        accessor = self.accessor

        assert_equal(
            accessor.getContainer('/test/path/toFile'),
            '/test/path'
        )

        assert_equal(
            accessor.getContainer('/test/path/toDir/'),
            '/test/path'
        )
        
        assert_equal(
            accessor.getContainer('/file'),
            '/'
        )

        # Fail if parent container cannot be found.
        with assert_raises(ftrack.AccessorParentResourceNotFoundError):
            accessor.getContainer('/')
