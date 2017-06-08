import dropbox
import ftrack


class DropboxFile(ftrack.String):
    '''Dropbox Buffered File.'''

    def __init__(self, client, resourceIdentifier, mode='rb', **kwargs):
        '''Initialise Dropbox file with a *client*, a *resourceIdentifier*.'''
        self.client = client
        self.resourceIdentifier = resourceIdentifier
        self.mode = mode
        self._hasRead = False
        super(DropboxFile, self).__init__(**kwargs)

    def flush(self):
        '''Flush all changes.'''
        super(DropboxFile, self).flush()

        # TODO: Handle other modes.
        if self.mode == 'wb':
            self._write()

    def read(self):
        '''Read all remote content from resourceIdentifier into wrapped_file.'''
        if not self._hasRead:
            position = self.tell()
            self.wrapped_file.seek(0)

            response = self.client.get_file(self.resourceIdentifier)
            self.wrapped_file.write(response.read())
            self.seek(position)

            self._hasRead = True

        return self.wrapped_file.read()

    def _write(self):
        '''Write current data to remote *resourceIdentifier*.'''
        position = self.tell()
        self.seek(0)
        self.client.put_file(
            self.resourceIdentifier, self.wrapped_file, overwrite=True
        )
        self.seek(position)


class DropboxAccessor(ftrack.Accessor):
    '''Provide Dropbox access to a location.'''

    def __init__(self, access_token, **kwargs):
        self.client = None
        self.client.connect(access_token)
        super(DropboxAccessor, self).__init__(**kwargs)

    def _getMetadata(self, resourceIdentifier):
        '''Return metadata for *resourceIdentifier*.'''
        metadata = {}
        try:
            metadata = self.client.metadata(resourceIdentifier)
        except dropbox.ErrorResponse, error:
            if error.status != 404:
                raise
        return metadata

    def list(self, resourceIdentifier):
        '''Return list of entries in *resourceIdentifier* container.'''
        listing = []
        try:
            meta = self.client.metadata(resourceIdentifier)
        except dropbox.rest.ErrorResponse, error:
            if error.status == 404:
                raise ftrack.AccessorResourceNotFoundError(resourceIdentifier)
            raise

        for content in meta.get('contents', []):
            contentPath = content.get('path')
            if contentPath:
                listing.append(contentPath)

        return listing

    def exists(self, resourceIdentifier):
        '''Return if *resourceIdentifier* is valid and exists in location.'''
        metadata = self._getMetadata(resourceIdentifier)
        result = bool(metadata)
        return result

    def isFile(self, resourceIdentifier):
        '''Return whether *resourceIdentifier* refers to a file.'''
        metadata = self._getMetadata(resourceIdentifier)
        result = not metadata.get('is_dir', True)
        return result

    def isSequence(self, resourceIdentifier):
        '''Return whether *resourceIdentifier* refers to a file sequence.'''
        raise ftrack.AccessorUnsupportedOperationError('isSequence')

    def isContainer(self, resourceIdentifier):
        '''Return whether *resourceIdentifier* refers to a directory.'''
        metadata = self._getMetadata(resourceIdentifier)
        return metadata.get('is_dir', False)

    def remove(self, resourceIdentifier):
        '''Remove *resourceIdentifier*.

        Raise :py:class:`~ftrack.ftrackerror.AccessorResourceNotFoundError` if
        *resourceIdentifier* does not exist.

        '''

        # TODO: Check if the directory is empty before deleting.
        try:
            self.client.file_delete(resourceIdentifier)
        except dropbox.rest.ErrorResponse, error:
            if error.status == 404:
                raise ftrack.AccessorResourceNotFoundError(resourceIdentifier)
            raise

    def getContainer(self, resourceIdentifier):
        '''Return resourceIdentifier of container for *resourceIdentifier*.

        Raise
        :py:class:`~ftrack.ftrackerror.AccessorParentResourceNotFoundError` if
        container of *resourceIdentifier* could not be determined.

        '''

        resourceIdentifier = resourceIdentifier.rstrip('/')
        container = resourceIdentifier.rpartition('/')[0]

        if not self.isContainer(container):
            raise ftrack.AccessorParentResourceNotFoundError(
                resourceIdentifier=resourceIdentifier
            )

        return container

    def makeContainer(self, resourceIdentifier, recursive=True):
        '''Make a container at *resourceIdentifier*.'''
        if not recursive:
            raise ftrack.AccessorUnsupportedOperationError(
                msg='Dropbox API only supports recursive container creation.'
            )

        try:
            self.client.file_create_folder(resourceIdentifier)
        except dropbox.rest.ErrorResponse, error:

            # Ignore errors about existing directories.
            if error.status == 403:
                pass
            raise

    def getAccessPath(self, path):
        '''Return a version of *path* for local access if possible.'''

        return path

    def open(self, resourceIdentifier, mode='rb'):
        '''Return :py:class:`~ftrack.Data` for *resourceIdentifier*.'''

        return DropboxFile(self.client, resourceIdentifier, mode)
