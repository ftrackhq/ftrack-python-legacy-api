# :coding: utf-8
# :copyright: Copyright (c) 2013 ftrack

import os
import tempfile

import ftrack

from .tools import ok_, assert_equal, assert_raises


class TestDiskAccessor(object):
    '''Test disk accessor.'''

    def setUp(self):
        '''Perform per test setup.'''

    def tearDown(self):
        '''Perform per test teardown.'''

    def testGetFilesystemPath(self):
        '''Convert paths to filesystem paths.'''
        temporary_path = tempfile.mkdtemp()
        accessor = ftrack.DiskAccessor(temporary_path)
    
        # Absolute paths outside of configured prefix fail.
        with assert_raises(ftrack.AccessorFilesystemPathError):
            accessor.getFilesystemPath(os.path.join('/', 'test', 'foo.txt'))

        # Absolute root path.
        assert_equal(accessor.getFilesystemPath(temporary_path), temporary_path)

        # Absolute path within prefix.
        assert_equal(
            accessor.getFilesystemPath(
                os.path.join(temporary_path, 'test.txt')
            ),
            os.path.join(temporary_path, 'test.txt')
        )

        # Relative root path
        assert_equal(accessor.getFilesystemPath(''), temporary_path)

        # Relative path for file at root
        assert_equal(accessor.getFilesystemPath('test.txt'),
                     os.path.join(temporary_path, 'test.txt'))
        
        # Relative path for file in subdirectory
        assert_equal(accessor.getFilesystemPath('test/foo.txt'),
                     os.path.join(temporary_path, 'test', 'foo.txt'))
        
        # Relative path non-collapsed
        assert_equal(accessor.getFilesystemPath('test/../foo.txt'),
                     os.path.join(temporary_path, 'foo.txt'))
        
        # Relative directory path without trailing slash
        assert_equal(accessor.getFilesystemPath('test'),
                     os.path.join(temporary_path, 'test'))
        
        # Relative directory path with trailing slash
        assert_equal(accessor.getFilesystemPath('test/'),
                     os.path.join(temporary_path, 'test'))

    def testList(self):
        '''List entries.'''
        temporary_path = tempfile.mkdtemp()
        accessor = ftrack.DiskAccessor(temporary_path)
        
        # File in root directory
        assert_equal(accessor.list(''), [])
        data = accessor.open('test.txt', 'w+')
        data.close()
        assert_equal(accessor.list(''), ['test.txt'])

        # File in subdirectory
        accessor.makeContainer('test_dir')
        assert_equal(accessor.list('test_dir'), [])
        data = accessor.open('test_dir/test.txt', 'w+')
        data.close()

        listing = accessor.list('test_dir')
        assert_equal(listing, ['test_dir/test.txt'])

        # Is a valid resource
        assert_equal(accessor.exists(listing[0]), True)

    def testExists(self):
        '''Check whether path exists.'''
        temporary_path = tempfile.mkdtemp()
        accessor = ftrack.DiskAccessor(temporary_path)
        
        _, temporary_file = tempfile.mkstemp(dir=temporary_path)
        assert_equal(accessor.exists(temporary_file), True)

        # Missing path
        assert_equal(accessor.exists(
            'non-existant.txt'
        ), False)

    def testIsFile(self):
        '''Check whether path is a file.'''
        temporary_path = tempfile.mkdtemp()
        accessor = ftrack.DiskAccessor(temporary_path)
        
        _, temporary_file = tempfile.mkstemp(dir=temporary_path)
        assert_equal(accessor.isFile(temporary_file), True)

        # Missing path
        assert_equal(accessor.isFile('non-existant.txt'), False)
        
        # Directory
        temporary_directory = tempfile.mkdtemp(dir=temporary_path)
        assert_equal(accessor.isFile(temporary_directory), False)
        
    def testIsContainer(self):
        '''Check whether path is a container.'''
        temporary_path = tempfile.mkdtemp()
        accessor = ftrack.DiskAccessor(temporary_path)
        
        temporary_directory = tempfile.mkdtemp(dir=temporary_path)
        assert_equal(accessor.isContainer(temporary_directory), True)
        
        # Missing path
        assert_equal(accessor.isContainer('non-existant'), False)
        
        # File
        _, temporary_file = tempfile.mkstemp(dir=temporary_path)
        assert_equal(accessor.isContainer(temporary_file), False)

    def testIsSequence(self):
        '''Check whether path is a sequence.'''
        temporary_path = tempfile.mkdtemp()
        accessor = ftrack.DiskAccessor(temporary_path)
            
        with assert_raises(ftrack.AccessorUnsupportedOperationError):
            accessor.isSequence('foo.%04d.exr')
        
    def testOpen(self):
        '''Open file.'''
        temporary_path = tempfile.mkdtemp()
        accessor = ftrack.DiskAccessor(temporary_path)
        
        with assert_raises(ftrack.AccessorResourceNotFoundError):
            accessor.open('test.txt', 'r')
        
        data = accessor.open('test.txt', 'w+')
        assert_equal(isinstance(data, ftrack.Data), True)
        assert_equal(data.read(), '')
        data.write('test data')
        data.close()
        
        data = accessor.open('test.txt', 'r')
        assert_equal(data.read(), 'test data')
        data.close()
    
    def testRemove(self):
        '''Delete path.'''
        temporary_path = tempfile.mkdtemp()
        accessor = ftrack.DiskAccessor(temporary_path)
        
        _, temporary_file = tempfile.mkstemp(dir=temporary_path)
        accessor.remove(temporary_file)
        assert_equal(os.path.exists(temporary_file), False)
        
        temporary_directory = tempfile.mkdtemp(dir=temporary_path)
        accessor.remove(temporary_directory)
        assert_equal(os.path.exists(temporary_directory), False)
        
    def testMakeContainer(self):
        '''Create container.'''
        temporary_path = tempfile.mkdtemp()
        accessor = ftrack.DiskAccessor(temporary_path)
        
        accessor.makeContainer('test')
        assert_equal(os.path.isdir(os.path.join(temporary_path, 'test')), True)
        
        # Recursive
        accessor.makeContainer('test/a/b/c')
        assert_equal(
            os.path.isdir(os.path.join(temporary_path, 'test', 'a', 'b', 'c')),
            True
        )
        
        # Non-recursive fail
        with assert_raises(ftrack.AccessorParentResourceNotFoundError):
            accessor.makeContainer('test/d/e/f', recursive=False)
        
        # Existing succeeds
        accessor.makeContainer('test/a/b/c')

    def testGetContainer(self):
        '''Get container from resourceIdentifier.'''
        # With prefix.
        temporary_path = tempfile.mkdtemp()
        accessor = ftrack.DiskAccessor(prefix=temporary_path)

        assert_equal(
            accessor.getContainer(os.path.join('test', 'a')),
            'test'
        )

        assert_equal(
            accessor.getContainer(os.path.join('test', 'a/')),
            'test'
        )

        assert_equal(
            accessor.getContainer('test'),
            ''
        )

        with assert_raises(ftrack.AccessorParentResourceNotFoundError):
            accessor.getContainer('')

        with assert_raises(ftrack.AccessorParentResourceNotFoundError):
            accessor.getContainer(temporary_path)

        # Without prefix.
        accessor = ftrack.DiskAccessor(prefix='')

        assert_equal(
            accessor.getContainer(os.path.join(temporary_path, 'test', 'a')),
            os.path.join(temporary_path, 'test')
        )

        assert_equal(
            accessor.getContainer(os.path.join(temporary_path, 'test', 'a/')),
            os.path.join(temporary_path, 'test')
        )

        assert_equal(
            accessor.getContainer(os.path.join(temporary_path, 'test')),
            temporary_path
        )
