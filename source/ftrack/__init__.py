# :coding: utf-8
# :copyright: Copyright (c) ftrack

import os
import sys

# Set the default ftrack server and API key variables to use if no matching
# environment variables are found.
os.environ.setdefault('FTRACK_SERVER', 'https://YOUR-FTRACK-SERVER')
os.environ.setdefault('FTRACK_APIKEY', 'YOUR-API-KEY')

# Honor the legacy FTRACK_PROXY environment variable.

_proxy_variables = (
    'https_proxy',
    'http_proxy'
)

if 'FTRACK_PROXY' in os.environ and os.environ.get('FTRACK_PROXY'):
    for variable in _proxy_variables:
        os.environ.setdefault(
            variable, os.environ.get('FTRACK_PROXY')
        )

elif set(_proxy_variables).intersection(os.environ):
    # If http_proxy and / or https_proxy environment variables are set
    # update FTRACK_PROXY with the value. If both exist https_proxy win's.
    for variable in [variable for variable in _proxy_variables if os.environ.get(variable)]:
        os.environ.setdefault(
            'FTRACK_PROXY', os.environ.get(variable)
        )

# Import core ftrack functionality into top level namespace.
from FTrackCore import *
