

class Plugin(object):
    '''Plugin.'''

    def getName(self):
        '''Return plugin name.'''
        return 'plugin_b'


def register(registry, **kw):
    '''Register plugin.'''
    registry.add(Plugin())
