..
    :copyright: Copyright (c) 2014 ftrack

.. _developing/legacy/reviewing/hosting_review_files:

********************
Hosting review files
********************

Setting up the server
=====================

.. note::

    If you have already setup a :ref:`administering/local_file_server` it can be
    configured to handle web reviewable files. Please contact ftrack support
    for more information.

By default ftrack handles hosting of web reviewable files. If you for some
reason want to host the files yourself you can set up your own server.

This can be done by using either an `Apache <http://httpd.apache.org/>`_
or `nginx <http://nginx.org/en/>`_ server. The examples uses an
`Apache <http://httpd.apache.org/>`_ server.

Install and setup the server of your choice. Once the server is up and running
you need to configure the web server to serve the encoded video files using a
CORS header that allows video data to be retrieved. This is needed to be able
to save frame annotations.

The following headers should be set::

    Access-Control-Allow-Origin: *
    Access-Control-Allow-Methods: POST, GET, OPTIONS
    Access-Control-Allow-Headers: Referer,Accept-Encoding,Range,Authorization,Content-Type,Accept,Origin,User-Agent,DNT,Cache-Control,X-Mx-ReqToken,Keep-Alive,X-Requested-With,If-Modified-Since

​This can be configured in your web server configuration, for Apache you can use
`mod_headers <http://httpd.apache.org/docs/2.2/mod/mod_headers.html>`_ and use
the Header set directive in .htaccess or (virtual) host configuration,
for example::

    Header set Access-Control-Allow-Origin "*"
    Header set Access-Control-Allow-Methods: POST, GET, OPTIONS
    Header set Access-Control-Allow-Headers: Referer,Accept-Encoding,Range,Authorization,Content-Type,Accept,Origin,User-Agent,DNT,Cache-Control,X-Mx-ReqToken,Keep-Alive,X-Requested-With,If-Modified-Since

When added restart your server and validate that your server sends the correct
headers. You do this by using curl to fetch the headers and check that the
output includes the headers specified. Additionally, make sure that the correct
MIME type is set in the Content-type header::

    curl -I http://your-hosting-server/path/to/video.mp4

.. note::
    
    To get the correct Content-Type you can use the
    `mod_mime <http://httpd.apache.org/docs/current/mod/mod_mime.html>`_
    Apache module

Publish components for review
=============================

To add a playable component on a version we simply need to create a new
component, add it to the review location and set some additional meta data
used by the player.

.. code-block:: python

    version = # Retrieve or create version.
    review_location = session.query('Location where name is "ftrack.review"').one()
    filepath = 'http://your-hosting-server/file.mp4'

    component = version.create_component(
        path=filepath,
        data={
            'name': 'ftrackreview-mp4'
        },
        location=review_location
    )

    # Meta data needs to contain *frameIn*, *frameOut* and *frameRate*.
    component['metadata']['ftr_meta'] = json.dumps({
        'frameIn': 0,
        'frameOut': 150,
        'frameRate': 25
    })

    component.session.commit()

.. note::

    For the component to play in the web browser, meta data with key `ftr_meta`
    need to exist on the component.

To publish an image for review the steps are similar:

.. code-block:: python

    version = # Retrieve or create a version you want to use
    review_location = session.query('Location where name is "ftrack.review"').one()
    filepath = 'http://your-hosting-server/image.jpg'

    component = version.create_component(
        path=filepath,
        data={
            'name': 'ftrackreview-image'
        },
        location=review_location
    )

    # Meta data needs to contain *format*.
    component['metadata']['ftr_meta'] = json.dumps({
        'format': 'image'
    })

    component.session.commit()

.. note::

    Make sure to use the pre-defined component names `ftrackreview-mp4`,
    `ftrackreview-webm` and `ftrackreview-image`. They are used to identify
    playable components in ftrack.

.. note::
    
    The `ftrack.review` location is an unmanaged location which requires
    absolute urls.
