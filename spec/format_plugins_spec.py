from hookshub.plugins import PluginManager
from hookshub.hook import Hook
from hookshub.hooks.github import GitHubUtil

from expects import *
from mock import patch, Mock


def ok():
    return True


class TestHook(Hook):
    __module__ = 'spec.format_plugins_spec'

    def __init__(self):
        super(TestHook, self).__init__(
            ok, GitHubUtil.events['EVENT_PULL_REQUEST']
        )
        self.enable()


plugins = PluginManager()

with description('PluginManager'):
    with context('Register plugins'):
        with it('Must add new hook on PluginManager'):
            from collections import namedtuple
            with patch("hookshub.plugins.InstanceManager.get") as pm_get:
                pm_get.start()
                hook_inst = TestHook()
                pm_get.return_value = hook_inst
                # If register is successfull, it'll return the same class
                expect(plugins.register(TestHook)).to(equal(TestHook))
                pm_get.stop()
            # Manual "register" process
            cls_name = '%s.%s' % (
                TestHook.__module__, TestHook.__name__
            )
            hook_name = cls_name.replace('.', '_')
            hook_data = namedtuple(
                hook_name,
                'name, hook, event, repository, branch'
            )
            hook_data.name = hook_name
            hook_data.hook = hook_inst
            hook_data.event = hook_inst.event
            hook_data.repository = hook_inst.repository
            hook_data.branch = hook_inst.branch

            # Compare manual and PluginManager
            plugin = plugins.get_hooks()[0]
            expect(len(plugins.get_hooks())).to(equal(1))
            expect(plugin.name).to(equal(hook_data.name))
            expect(plugin.hook).to(equal(hook_data.hook))
            expect(plugin.event).to(equal(hook_data.event))
            expect(plugin.repository).to(equal(hook_data.repository))
            expect(plugin.branch).to(equal(hook_data.branch))

        with it('Must update existing hook on PluginManager'):
            from collections import namedtuple
            # If register is successfull, it'll return the same class
            # Manual "register" process
            cls_name = '%s.%s' % (
                TestHook.__module__, TestHook.__name__
            )
            hook_name = cls_name.replace('.', '_')
            hook_data = namedtuple(
                hook_name,
                'name, hook, event, repository, branch'
            )
            hook_inst = TestHook()
            hook_data.name = hook_name
            hook_data.hook = hook_inst
            hook_data.event = hook_inst.event
            hook_data.repository = hook_inst.repository
            hook_data.branch = hook_inst.branch
            with patch("hookshub.plugins.import_module") as import_method:
                import_method.start()
                model = Mock()
                model.TestHook.return_value = hook_data
                import_method.return_value = model
                expect(plugins.register(TestHook)).to(equal(TestHook))
                import_method.stop()

            # Compare manual and PluginManager
            plugin = plugins.get_hooks()[0].hook
            # As we update the plugins, there should not exist any more hooks
            expect(len(plugins)).to(equal(1))
            expect(plugin.name).to(equal(hook_data.name))
            expect(plugin.hook).to(equal(hook_data.hook))
            expect(plugin.event).to(equal(hook_data.event))
            expect(plugin.repository).to(equal(hook_data.repository))
            expect(plugin.branch).to(equal(hook_data.branch))

    with context('Unregister plugins'):
        with it('must return "False" if hook does not exist'):

            class TotallyNotExistingHook(Hook):
                __module__ = 'spec.format_plugins_spec'

            res = plugins.unregister(TotallyNotExistingHook)
            expect(res).to(equal(False))

    with context('method __iter__ and __len__'):
        with it('must return an iterable with the same len as __len__ with'
                'all hooks in plugin manager'):
            expect(sum(1 for i in iter(plugins))).to(equal(len(plugins)))


