# :coding: utf-8
# :copyright: Copyright (c) 2017 ftrack

'''ftrack-python-legacy-api documentation build configuration file.'''

import os
import sys
import re

# -- General ------------------------------------------------------------------

# Inject source onto path so that autodoc can find it by default, but in such a
# way as to allow overriding location.
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'source'))
)


# Extensions.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'lowdown'
]


# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'ftrack-python-legacy-api'
copyright = u'2017, ftrack'

# Version
with open(
    os.path.join(os.path.join(
        os.path.dirname(__file__), '..', 'source',
        'FTrackCore', 'api', 'version_data.py'
    ))
) as _version_file:
    _version = re.match(
        r'.*ftrackVersion = \'(.*?)\'', _version_file.read(), re.DOTALL
    ).group(1)

version = _version
release = _version

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_template']

# A list of prefixes to ignore for module listings.
modindex_common_prefix = [
    'ftrack_python_legacy_api.'
]

# -- HTML output --------------------------------------------------------------

# on_rtd is whether currently on readthedocs.org
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # only import and set the theme if building docs locally
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_static_path = ['_static']

# If True, copy source rst files to output for reference.
html_copy_source = True


# -- Autodoc ------------------------------------------------------------------

autodoc_default_flags = ['members', 'undoc-members']
autodoc_member_order = 'bysource'


def autodoc_skip(app, what, name, obj, skip, options):
    '''Don't skip __init__ method for autodoc.'''
    if name == '__init__':
        return False

    return skip


# -- Intersphinx --------------------------------------------------------------

intersphinx_mapping = {
    'python': (
        'http://docs.python.org/', None
    ),
    'ftrack': (
        'http://ftrack.rtd.ftrack.com/en/stable', None
    ),
    'ftrack-connect': (
        'http://rtd.ftrack.com/docs/ftrack-connect/en/latest/', None
    ),
}


# -- Todos ---------------------------------------------------------------------

todo_include_todos = True


# -- Setup --------------------------------------------------------------------

def setup(app):
    app.connect('autodoc-skip-member', autodoc_skip)


# -- Deprecation warning ------------------------------------------------------

rst_prolog = """
.. warning::
   Legacy python api are soon to be deprecated and should avoid to use them in production.
   Please use the `new api <https://bitbucket.org/ftrack/ftrack-python-api/src/master/>`_ available.
"""