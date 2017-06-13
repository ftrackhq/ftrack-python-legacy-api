# :coding: utf-8
# :copyright: Copyright (c) ftrack

import os
import sys

# Set the default ftrack server and API key variables to use if no matching
# environment variables are found.
os.environ.setdefault('FTRACK_SERVER', 'https://YOUR-FTRACK-SERVER')
os.environ.setdefault('FTRACK_APIKEY', 'YOUR-API-KEY')

# Honor the legacy FTRACK_PROXY environment variable.
if 'FTRACK_PROXY' in os.environ and os.environ.get('FTRACK_PROXY'):
    for variable in ('http_proxy', 'https_proxy'):
        os.environ.setdefault(
            variable, os.environ.get('FTRACK_PROXY')
        )

# Import core ftrack functionality into top level namespace.
from FTrackCore import *
