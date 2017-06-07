..
    :copyright: Copyright (c) 2014 ftrack

********************************
Writing a custom accessor plugin
********************************

.. warning::
    
    The Dropbox API has changed since the tutorial was written, and it does not
    work with the current API. The tutorial was written as a guide on how to
    write a custom accessor and is not intended to be used in production.

    The easiest way to use Dropbox storage for your location is simply to
    configure a Centralized storage scenario, configured with the prefix where
    dropbox stores the files and leveraging Dropbox for syncing files. Though
    this currently has some restrictions: all users need to have the same
    dropbox mount point and the files need to be present on the local machine
    (though, you can use selective sync to only store data for certain
    projects).

This tutorial is a guide on how you write a custom accessor plugin for use with 
ftrack locations and the ftrack API. Before you read this guide, make sure you 
read through the :ref:`using/locations` and :doc:`tutorial`.

Introduction
============

We will be writing an accessor for Dropbox (`www.dropbox.com 
<https://www.dropbox.com/>`_). To follow along with the examples, you will need 
an account and the Dropbox Python SDK installed. You can obtain it from 
`their site <https://www.dropbox.com/developers/core/sdks/python>`_, or install 
it using pip.

.. code-block:: bash
    
    $ pip install dropbox

The Accessor's responsability is to provide data access to a location. 
A location represents a specific storage, but access to that storage may
vary. For example, both local filesystem and FTP access may be possible for
the same storage. An accessor implements these different ways of accessing
the same data location.

As different accessors may access the same location, only part of a data
path that is commonly understood may be stored in the database. The format
of this path should be a contract between the accessors that require access
to the same location and is left as an implementation detail. As such, this
system provides no guarantee that two different accessors can provide access
to the same location, though this is a clear goal. The path stored centrally
is referred to as the **resource identifier** and should be used when
calling any of the accessor methods that accept a ``resourceIdentifier``
argument.


Getting started
===============

Start out by importing the ftrack module and creating a class which
implements the ``ftrack.Accessor`` interface.

.. code-block:: python

    import ftrack

    class DropboxAccessor(ftrack.Accessor):
        '''Provide Dropbox access to a location.'''

Then, add a constructor which takes as input an access token and creates a 
`DropboxClient`_, which is used to commuincate with Dropbox.

.. literalinclude:: /resource/dropbox_accessor.py
    :language: python
    :lines: 50-53

Generating an access token
--------------------------
To access the Dropbox API you will need to generate an access token. To do so,
first need to create an `Dropbox API app 
<https://www.dropbox.com/developers/apps/create>`_. The application should have
access to *Files and datastores* and be *limited to its own, private folder*. 
Name the application something, e.g. ``ftrack-test-location``, and write down
the **app key** and **app secret**. To generate the access key, you can 
download the file :download:`generate_dropbox_token.py 
</resource/generate_dropbox_token.py>` and run it as:

.. code-block:: bash

    $ python generate_dropbox_token.py <app_key> <app_secret>

It will open up a web browser, where you can give the application access to 
your Dropbox. Copy the returned code and paste it into the terminal to
generate the access token. Save the generated token somewhere, 
you will need it to instantiate the ``DropboxAccessor``


Implementing the interface
==========================

Listing files
-------------

Now we can start to implement the methods required to implement the ``Accessor`` 
interface. Let's start off with the :py:meth:`list` method.

.. code-block:: python

    def list(self, resourceIdentifier):
        listing = []
        meta = self.client.metadata(resourceIdentifier)
        for content in meta.get('contents', []):
            contentPath = content.get('path')
            if contentPath:
                listing.append(contentPath)

        return listing


Time to test our new method. Save the file as ``dropbox_accessor.py`` and fire 
up a Python interpreter.

.. code-block:: python
    
    >>> from dropbox_accessor import DropboxAccessor
    >>> accessor = DropboxAccessor('YOUR ACCESS TOKEN')
    >>> accessor.list('/')
    []

The call should return an empty array. If it throws an Exception, double-check 
that the access token you provided is valid. If everything is working, let's 
try an invalid resource and see what happens.

.. code-block:: python

    >>> accessor.list('/test_folder')
    ...
    dropbox.rest.ErrorResponse: [404] u"Path '/test_folder' not found"

The call threw an exception, ``dropbox.rest.ErrorResponse``. While 
getting an exception for an invalid resource is expected, we should try to wrap
all common exceptions as accessor-specific variants. The following table shows 
all the accessor exceptions defined in the ftrack API along with a description 
of when to use them.

+-----------------------------------------------+--------------------------------------------------------------------+
| Exception Class                               | Description                                                        |
+===============================================+====================================================================+
| :py:exc:`ftrack.AccessorError`                | Base for errors associated with accessors.                         |
+-----------------------------------------------+--------------------------------------------------------------------+
| :py:exc:`AccessorOperationFailedError`        | Base for failed operations on accessors.                           |
+-----------------------------------------------+--------------------------------------------------------------------+
| :py:exc:`AccessorUnsupportedOperationError`   | Raise when operation is unsupported.                               |
+-----------------------------------------------+--------------------------------------------------------------------+
| :py:exc:`AccessorPermissionDeniedError`       | Raise when permission denied.                                      |
+-----------------------------------------------+--------------------------------------------------------------------+
| :py:exc:`AccessorResourceIdentifierError`     | Raise when a error related to a resourceIdentifier occurs.         |
+-----------------------------------------------+--------------------------------------------------------------------+
| :py:exc:`AccessorFilesystemPathError`         | Raise when a error related to an accessor filesystem path occurs.  |
+-----------------------------------------------+--------------------------------------------------------------------+
| :py:exc:`AccessorResourceError`               | Base for errors associated with specific resource.                 |
+-----------------------------------------------+--------------------------------------------------------------------+
| :py:exc:`AccessorResourceNotFoundError`       | Raise when a required resource is not found.                       |
+-----------------------------------------------+--------------------------------------------------------------------+
| :py:exc:`AccessorParentResourceNotFoundError` | Raise when a parent resource (such as directory) is not found.     |
+-----------------------------------------------+--------------------------------------------------------------------+
| :py:exc:`AccessorResourceInvalidError`        | Raise when a resource is not the right type.                       |
+-----------------------------------------------+--------------------------------------------------------------------+
| :py:exc:`AccessorContainerNotEmptyError`      | Raise when container is not empty.                                 |
+-----------------------------------------------+--------------------------------------------------------------------+


``AccessorResourceNotFoundError`` seems like a good fit. Lets update the ``list`` 
method to throw the appropriate exception if the directory is not found. We 
check so that the returned status code is 404, and otherwise re-raise the 
exception.

.. literalinclude:: /resource/dropbox_accessor.py
    :language: python
    :lines: 66-81
    :emphasize-lines: 4-9

Creating directories
--------------------

Our list function seems to be working, but we can't really tell unless we have 
something that it can list. So, let's continue by adding support for creating 
directories using our accessor. The ``Accessor`` interface declares the 
following abstract method.

.. code-block:: python

    @abstractmethod
    def makeContainer(self, resourceIdentifier, recursive=True):
        '''Make a container at *resourceIdentifier*.

        If *recursive* is True, also make any intermediate containers.

        '''

In the Dropbox API we can find the same functionality as the function 
`file_create_folder`_. We implement the method in our ``DropboxAccessor`` as:

.. literalinclude:: /resource/dropbox_accessor.py
    :language: python
    :pyobject: DropboxAccessor.makeContainer

Let's use our new functionality to create a directory which we can list. 

.. code-block:: python

    >>> accessor.makeDirectory('/test_dir')
    >>> accessor.list('/')
    [u'/test_dir']

It works! Let's create another directory to verify that we can create 
directories recursively.

.. code-block:: python

    >>> accessor.makeDirectory('/a/b/c')
    >>> accessor.list('/a')
    [u'/a/b']


Checking if something is a container
------------------------------------
Now that we can create containers, we can add a method to check if a resource 
is a container. The interface is defined in ``ftrack.Accessor`` as:

.. code-block:: python

    @abstractmethod
    def isContainer(self, resourceIdentifier):
        '''Return whether *resourceIdentifier* refers to a container.'''

The implementation should be quite straight forward. We utilize the ``metadata``
method in the dropbox SDK.

.. literalinclude:: /resource/dropbox_accessor.py
    :language: python
    :pyobject: DropboxAccessor._getMetadata

.. literalinclude:: /resource/dropbox_accessor.py
    :language: python
    :pyobject: DropboxAccessor.isContainer

To test the method, a existing and non-existing directory can be passed in.

.. code-block:: python

    >>> accessor.isContainer('/a')
    True
    >>> accessor.isContainer('/nonexistant')
    False

Obtaining containers 
--------------------

Next up is the ``getContainer`` method. It is responsible for retrieving the 
the container of a resource. The interface looks like this.

.. code-block:: python

    @abstractmethod
    def getContainer(self, resourceIdentifier):
        '''Return resourceIdentifier of container for *resourceIdentifier*.

        Raise 
        :py:class:`~ftrack.ftrackerror.AccessorParentResourceNotFoundError` if 
        container of *resourceIdentifier* could not be determined.

        '''

For a file, the method should return the container it is in and for containers, 
the method should return the parent container.

.. literalinclude:: /resource/dropbox_accessor.py
    :language: python
    :pyobject: DropboxAccessor.getContainer

.. code-block:: python

    >>> accessor.getContainer('/a/b')
    '/a'

Removing containers
--------------------

Now we need to be able to get rid of all of these junk containers. 
Let's implement the method `Accessor.remove`. The interface is declared as:

.. code-block:: python

    @abstractmethod
    def remove(self, resourceIdentifier):
        '''Remove *resourceIdentifier*.

        Raise :py:class:`~ftrack.ftrackerror.AccessorResourceNotFoundError` if
        *resourceIdentifier* does not exist.

        '''

We take the same approach as earlier and look through the Dropbox API for an 
appropriate method and find a good candidate in the `file_delete`_ function.
We use this function to implement our function.

.. literalinclude:: /resource/dropbox_accessor.py
    :language: python
    :pyobject: DropboxAccessor.remove

Now let's use our new method to remove everything. 

.. code-block:: python

    >>> for resource in accessor.list('/'):
    ...     print 'Removing:', resource
    ...     accessor.remove(resource)
    ... 
    Removing: /a
    Removing: /test_dir


Working with files
==================

Now that we can manage directories, let's continue on with files. Whenever a 
component is added to a location, it is the accessor's responsibility to 
provide data access for copying the data. The interface declares a method 
``open`` which should return an implementation of ``ftrack.Data``, 
a File-like object for manipulating data.

For a disk-based accessor, we could use ``ftrack.File`` which accepts a 
filesystem path and returns a wrapped File object. Also provided is 
``ftrack.String`` which wraps ``StringIO``, which we will use in this case.
For other File-like objects, you can use ``ftrack.FileWrapper``.

We declare a class, ``DropboxFile``, at the top of ``dropbox_accessor.py`` 
which inherits from ``ftrack.String`` and provides data acccess to a 
``resourceIdentifier`` using a ``client``. The ``read`` method uses the 
function `get_file`_ from the Dropbox SDK to retreive the contents from the 
remote storage to the local ``StringIO`` buffer. When the instance is 
``flush``-ed, the contents are written to the remote storage using `put_file`_.


.. literalinclude:: /resource/dropbox_accessor.py
    :language: python
    :pyobject: DropboxFile

The class is used in the ``open`` implementation in the following way.

.. literalinclude:: /resource/dropbox_accessor.py
    :language: python
    :pyobject: DropboxAccessor.open


exists, isFile and isSequence
-----------------------------
The remaining methods to fulfill the ``Accessor`` interface are ``exists``, 
``isFile`` and ``isSequence``. The first two are implemented in a 
similar way to ``isContainer`` by utilizing the metadata returned by the 
Dropbox SDK. ``isSequence`` is left as an unsupported 
operation for now.

.. literalinclude:: /resource/dropbox_accessor.py
    :language: python
    :pyobject: DropboxAccessor.exists

.. literalinclude:: /resource/dropbox_accessor.py
    :language: python
    :pyobject: DropboxAccessor.isFile

.. literalinclude:: /resource/dropbox_accessor.py
    :language: python
    :pyobject: DropboxAccessor.isSequence

Using the accessor
==================

Now that we have implemented our our dropbox accessor, we are ready to test it
out. The following example creates a location with the accessor and creates a 
component in the location. It then uses the accessor to retreive the contents 
of the component from the remote storage.

.. note:: 
    If you haven't been following along you can download the finished 
    accessor :download:`dropbox_accessor.py </resource/dropbox_accessor.py>`. 

.. warning:: 
    The Dropbox accessor is not ready for production use.

.. literalinclude:: /resource/dropbox_accessor_usage.py

.. _DropboxClient: https://www.dropbox.com/developers/core/docs/python#DropboxClient
.. _file_create_folder: https://www.dropbox.com/developers/core/docs/python#DropboxClient.file_create_folder
.. _file_create_folder: https://www.dropbox.com/developers/core/docs/python#DropboxClient.file_create_folder
.. _file_delete: https://www.dropbox.com/developers/core/docs/python#DropboxClient.file_delete
.. _put_file: https://www.dropbox.com/developers/core/docs/python#DropboxClient.put_file
.. _get_file: https://www.dropbox.com/developers/core/docs/python#DropboxClient.get_file

