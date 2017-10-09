from hookshub.plugins import PluginManager
from hookshub.hook import Hook
from hookshub.hooks.github import GitHubUtil

from expects import *
from mock import patch, Mock

_TEST_HOOK_VERSION = 123


def ok():
    return True


class TestHook(Hook):
    __module__ = 'hookshub.spec.format_plugins_spec'
    __version__ = _TEST_HOOK_VERSION

    def __init__(self):
        super(TestHook, self).__init__(
            method=ok, event=GitHubUtil.events['EVENT_PULL_REQUEST']
        )


plugins = PluginManager()

with description('PluginManager'):
    with context('Register plugins'):
        with it('Must add new hook on PluginManager'):
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

    with context('method get'):
        with it('Must return None when getting an unexisting hook'):
            class TotallyNotExistingHook(Hook):
                __module__ = 'hookshub.spec.format_plugins_spec'

            expect(plugins.get(TotallyNotExistingHook)).to(be_none)

        with it('Must return None when trying to import unimportable hook'):
            with patch("hookshub.plugins.import_module",
                       side_effect=Exception('Fail Import')) as import_method:
                expect(plugins.get(TestHook)).to(be_none)

    with context('Unregister plugins'):
        with it('must return "False" if hook does not exist'):
            class TotallyNotExistingHook(Hook):
                __module__ = 'hookshub.spec.format_plugins_spec'

            res = plugins.unregister(TotallyNotExistingHook)
            expect(res).to(equal(False))

        with it('must return "TestHook" if hook does unregister successfully'):
            from collections import namedtuple
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
                res = plugins.unregister(TestHook)
                expect(res).to(equal(TestHook))

    with context('method __iter__ and __len__'):
        with it('must return an iterable with the same len as __len__ with'
                'all hooks in plugin manager'):
            expect(sum(1 for i in iter(plugins))).to(equal(len(plugins)))

    with context('method all'):
        with it('must return all registered plugins with specified VERSION'
                'that are ENABLED'):
            
            class TestHookDisabled(Hook):
                __module__ = 'hookshub.spec.format_plugins_spec'
                __version__ = _TEST_HOOK_VERSION

                def __init__(self):
                    super(TestHookDisabled, self).__init__(
                        method=ok, event=GitHubUtil.events['EVENT_PULL_REQUEST']
                    )
                    self.disable()


            class TestHookVersion(Hook):
                __module__ = 'hookshub.spec.format_plugins_spec'
                __version__ = -1

                def __init__(self):
                    super(TestHookVersion, self).__init__(
                        method=ok, event=GitHubUtil.events['EVENT_PULL_REQUEST']
                    )
                    
            # Clean cache to test all the paths of method
            plugins.cache = None
            gen_hooks = plugins.all(version=_TEST_HOOK_VERSION)
            hooks = [h for h in gen_hooks]
            expect(len(hooks)).to(equal(0))
            # Register test plugin so there's a plugin with specified version
            from collections import namedtuple
            
            #       TestHook
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
            
            #       TestHook DISABLED
            cls_name = '%s.%s' % (
                TestHookDisabled.__module__, TestHook.__name__
            )
            hook_name = cls_name.replace('.', '_')
            hook_data_disabled = namedtuple(
                hook_name,
                'name, hook, event, repository, branch'
            )
            hook_inst_disabled = TestHookDisabled()
            hook_data_disabled.name = hook_name
            hook_data_disabled.hook = hook_inst_disabled
            hook_data_disabled.event = hook_inst_disabled.event
            hook_data_disabled.repository = hook_inst_disabled.repository
            hook_data_disabled.branch = hook_inst_disabled.branch
            
            #       TestHook VERSION
            cls_name = '%s.%s' % (
                TestHookVersion.__module__, TestHook.__name__
            )
            hook_name = cls_name.replace('.', '_')
            hook_data_version = namedtuple(
                hook_name,
                'name, hook, event, repository, branch'
            )
            hook_inst_version = TestHookVersion()
            hook_data_version.name = hook_name
            hook_data_version.hook = hook_inst_version
            hook_data_version.event = hook_inst_version.event
            hook_data_version.repository = hook_inst_version.repository
            hook_data_version.branch = hook_inst_version.branch
            
            with patch("hookshub.plugins.import_module") as import_method:
                import_method.start()
                model = Mock()
                model.TestHook.return_value = hook_data
                model.TestHookDisabled.return_value = hook_data_disabled
                model.TestHookVersion.return_value = hook_data_version
                import_method.return_value = model

                # If register is successfull, it'll return the same class
                expect(plugins.register(TestHook)).to(equal(TestHook))
                expect(plugins.register(TestHookDisabled)).to(
                    equal(TestHookDisabled))
                expect(plugins.register(TestHookVersion)).to(
                    equal(TestHookVersion))

                gen_hooks = plugins.all(version=_TEST_HOOK_VERSION)
                hooks = [h for h in gen_hooks]
                expect(len(hooks)).to(equal(1))
                expect(hooks[0]).to(equal(hook_inst))
                # After first getting, result should be in cache
                gen_hooks = plugins.all(version=_TEST_HOOK_VERSION)
                hooks_cache = [h for h in gen_hooks]
                expect(hooks_cache).to(equal(hooks))
                import_method.stop()
