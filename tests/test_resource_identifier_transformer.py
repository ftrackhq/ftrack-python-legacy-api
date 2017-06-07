# :coding: utf-8
# :copyright: Copyright (c) 2014 FTrack

from ftrack import ResourceIdentifierTransformer

from .tools import assert_equal


class TestResourceIdentifierTransformer(object):
    '''Test ResourceIdentifierTransformer.'''

    def testEncode(self):
        '''Encode resource identifier.'''
        resourceIdentifier = 'test.identifier'
        transformer = ResourceIdentifierTransformer()

        assert_equal(transformer.encode(resourceIdentifier), resourceIdentifier)

    def testEncodeWithContext(self):
        '''Encode resource identifier using context.'''
        resourceIdentifier = 'test.identifier'
        transformer = ResourceIdentifierTransformer()

        assert_equal(
            transformer.encode(resourceIdentifier, context={}),
            resourceIdentifier
        )

    def testDecodeWithoutContext(self):
        '''Decode resource identifier without context.'''
        resourceIdentifier = 'test.identifier'
        transformer = ResourceIdentifierTransformer()

        assert_equal(transformer.decode(resourceIdentifier), resourceIdentifier)

    def testDecodeWithContext(self):
        '''Decode resource identifier using context.'''
        resourceIdentifier = 'test.identifier'
        transformer = ResourceIdentifierTransformer()

        assert_equal(
            transformer.decode(resourceIdentifier, context={}),
            resourceIdentifier
        )
