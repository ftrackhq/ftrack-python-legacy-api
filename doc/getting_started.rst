..
    :copyright: Copyright (c) 2014 ftrack

.. _developing/legacy/getting_started:

***************
Getting started
***************

The :term:`Python` :term:`API` can be used to communicate with a ftrack server
from within any software that supports :term:`Python`.

.. _developing/legacy/getting_started/quick_start_api_code_example:

Quick start API code example
============================

Before being able to communicate with a ftrack server from a Python script, the
Python API has to be set up. Follow the 5 simple steps below to get started:

#. Install the Python API using pip

   .. code-block:: bash

      pip install ftrack-python-legacy-api


#. Open your favorite text editor, copy and paste the following code block into
   a new file and change the three lines in the top to be valid for your server.
   See the notes below for comments on those lines. Save the file in the same
   directory as before.

   .. code-block:: python

      import os

      os.environ['FTRACK_SERVER'] = 'https://<my name>.ftrackapp.com'
      os.environ['FTRACK_APIKEY'] = '<my API key>'
      os.environ['LOGNAME'] = '<my username>'

      import ftrack

      for project in ftrack.getProjects():
          print project.getFullName()

   * The :envvar:`FTRACK_SERVER` variable should point to your server, for
     example: ``https://<my name>.ftrackapp.com``.

   * The :envvar:`FTRACK_APIKEY` variable should be set to an API key. You can
     get an API key for your server in two ways:

     1. Copy your private API key from your My account page by clicking your
        avatar picture in the top right corner of the web interface and
        selecting :guilabel:`My account`. If using your private API key, make
        sure you set the username you are signing in to ftrack with in the next
        step.

     2. Copy an existing API key or add a new API key from the
        :menuselection:`System settings --> Security --> API keys` page.

   * The :envvar:`LOGNAME` variable should be set to your username on
     your ftrack server. This can also be copied from :guilabel:`My account`.

#. Launch a terminal window or Command Prompt and navigate to the directory
   where you saved the file. Enter ``python myfile.py`` where :file:`myfile.py`
   is the filename of the Python file you just created, and press :kbd:`Enter`.

#. If the output in the terminal contains the names of all your projects, you
   have successfully set up your API and can start writing more advanced
   Python scripts! Happy coding!

If you need any help, let us know by sending an email to support@ftrack.com.

You are now ready to start developing with ftrack and can continue to other
pages. For more information on Security and API keys, continue reading this
page.

.. _developing/legacy/getting_started/security:

Security and API keys
=====================

The :term:`API` will communicate with the server as the currently logged in
user. :term:`API` keys can be created and managed in the
:menuselection:`System settings --> Security --> API keys` section in the ftrack
web interface.

It is sometimes useful to override the user that is used. The environment
variables :envvar:`LOGNAME`, :envvar:`USER`, :envvar:`LNAME` and
:envvar:`USERNAME` are used in that order to figure out the current user as
specified by the :term:`Python` standard :py:mod:`getpass` module.

So, for example, setting :envvar:`LOGNAME` to the desired username will cause
all actions through the :term:`API` to be performed as that user.

:term:`API` keys are used to improve security when using the :term:`API` as no
password is needed to communicate with the server. The :term:`API` key acts as a
password that can be disabled or replaced if needed.

The :term:`API` key is configured by setting the environment
variable :envvar:`FTRACK_APIKEY`.

API setup
=========

The :term:`Python` :term:`API` is comprised of two parts:

    * **ftrack.py** A simple wrapper that allows setting of a few key
      environment variables and which imports the entire contents of the
      FTrackCore.egg under the ``ftrack`` namespace. :envvar:`FTRACK_SERVER` and
      :envvar:`FTRACK_APIKEY` are defined here and should be set to point to
      your server (or commented out if you want to use a different method for
      setting these).
    * **FTrackCore.egg** A zipped package that contained the actual files used
      by the :term:`API`. When updating the server version FTrackCore.egg will
      also need to be updated.

.. note::

   The Python API can be downloaded from 
   :menuselection:`System Settings --> General Settings --> About`, or by
   navigating to the URL ``<YOUR_FTRACK_SERVER_URL>/python-api.tar``.
   Replace ``<YOUR_FTRACK_SERVER_URL>`` with the address to your ftrack
   server, e.g. my-company.ftrackapp.com.

The following environment variables can be used to configure :term:`API` usage:

.. envvar:: FTRACK_SERVER

    The server URL including protocol, for example ``https://my.ftrackapp.com``.

.. envvar:: FTRACK_APIKEY

    The :term:`API` key to use when authenticating.

.. envvar:: FTRACK_PROXY

    An optional proxy URL to use if required.

.. envvar:: FTRACK_BULK

    Set to 'true' to skip feed generation and push notifications. Useful for
    improving performance in scripts that perform bulk inserts.

    .. warning::

        Only use for test purposes.

In addition, you must place the ftrack modules on the :envvar:`PYTHONPATH`.

With the environment configured, open a :term:`Python` shell and import ftrack
to get started::

    import ftrack

The ftrack module works with :term:`Python` 2.6+
