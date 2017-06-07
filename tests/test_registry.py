
import os

from ftrack import Registry

from .tools import ok_, assert_equal


class Plugin(object):
    '''Test plugin.'''

    def __init__(self, name):
        '''Initialise plugin with *name*.'''
        super(Plugin, self).__init__()
        self._name = name

    def getName(self):
        '''Return plugin name.'''
        return self._name


class TestRegistry(object):
    '''Test Registry.'''

    def __init__(self):
        '''Initialise test.'''
        self.basePath = os.path.join(os.path.dirname(__file__))
        self.pluginPaths = [os.path.join(self.basePath, 'plugin', 'registry')]

    def setUp(self):
        '''Perform per test setup.'''

    def tearDown(self):
        '''Perform per test teardown.'''
    
    def testDiscover(self):
        '''Discover plugins under paths.'''
        registry = Registry(paths=self.pluginPaths)
        assert_equal(len(registry), 0)

        registry.discover()
        assert_equal(len(registry), 2)

    def testGet(self):
        '''Retrieve plugin by name.'''
        registry = Registry(paths=self.pluginPaths)
        registry.discover()
        assert_equal(registry.get('plugin_a').getName(), 'plugin_a')

    def testGetNoMatch(self):
        '''Retrieve plugin by name when no plugin registered.'''
        registry = Registry(paths=self.pluginPaths)
        assert_equal(registry.get('plugin_a'), None)

    def testAdd(self):
        '''Add a new plugin.'''
        registry = Registry()
        assert_equal(registry.get('plugin_a'), None)
        plugin = Plugin('plugin_a')
        registry.add(plugin)
        assert_equal(registry.get('plugin_a'), plugin)

    def testDiscard(self):
        '''Discard a plugin.'''
        registry = Registry()
        plugin = Plugin('plugin_a')
        registry.add(plugin)
        assert_equal(registry.get('plugin_a'), plugin)

        registry.discard(plugin)
        assert_equal(registry.get('plugin_a'), None)

    def testIterate(self):
        '''Iterate over plugins.'''
        registry = Registry()

        plugin_a = Plugin('plugin_a')
        registry.add(plugin_a)

        plugin_b = Plugin('plugin_b')
        registry.add(plugin_b)

        assert_equal(len(registry), 2)
        assert_equal(registry.get('plugin_a'), plugin_a)
        assert_equal(registry.get('plugin_b'), plugin_b)

    def testCount(self):
        '''Retrieve number of plugins in registry.'''
        registry = Registry()
        assert_equal(len(registry), 0)

        registry.add(Plugin('plugin_a'))
        assert_equal(len(registry), 1)

        registry.add(Plugin('plugin_b'))
        assert_equal(len(registry), 2)

        registry.discard(registry.get('plugin_b'))
        assert_equal(len(registry), 1)

    def testContains(self):
        '''Return whether plugin in registry.'''
        registry = Registry()
        plugin = Plugin('plugin_a')

        assert_equal(plugin in registry, False)

        registry.add(plugin)

        assert_equal(plugin in registry, True)
