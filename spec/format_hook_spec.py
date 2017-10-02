from hookshub.plugins import PluginManager
from hookshub.hook import Hook
from hookshub.hook import get_hooks
from hookshub.hook import reload_hooks
from hookshub.hooks.github import GitHubUtil
from collections import namedtuple

from expects import *
from mock import patch, Mock

_TEST_HOOK_VERSION = 123


def ok(args):
    return True


class TestHook(Hook):
    __module__ = 'hookshub.spec.format_plugins_spec'
    __version__ = _TEST_HOOK_VERSION

    def __init__(self):
        super(TestHook, self).__init__(
            method=ok, event=GitHubUtil.events['EVENT_PULL_REQUEST']
        )


plugins = PluginManager()
test_hook = TestHook()

with description('HooksHub/Hook'):
    with context('Plugin Class'):
        with it(' must return property values'):
            expect(test_hook.title).to(equal(str(test_hook.__class__)))
            expect(test_hook.hook).to(equal(ok))
            expect(test_hook.event).to(equal(
                GitHubUtil.events['EVENT_PULL_REQUEST']))
            expect(test_hook.repository).to(be_false)
            expect(test_hook.branch).to(be_false)
            expect(test_hook.enabled).to(be_true)

        with it(' must return be enabled by default'):
            expect(test_hook.enabled).to(be_true)
            expect(test_hook.is_enabled()).to(be_true)

        with it(' must be disabled after running "disable" method'):
            expect(test_hook.disable()).to(be_false)
            expect(test_hook.is_enabled()).to(be_false)
            expect(test_hook.enabled).to(be_false)

        with it(' must be enabled after running "enable" method'):
            expect(test_hook.enable()).to(be_true)
            expect(test_hook.is_enabled()).to(be_true)
            expect(test_hook.enabled).to(be_true)

        with it(' must return a tunned argument dictionary with the webhook and'
                'config data specified to run the hook'):
            # Default return (no webhook or config)
            expect(test_hook.get_args()).to(equal({'Default': True}))
            # Only config
            expect(test_hook.get_args(conf=True)).to(equal({'conf': True}))
            # Only webhook
            expect(test_hook.get_args(webhook=True)).to(equal({'webhook': True}))
            # Both
            expect(test_hook.get_args(webhook=True, conf=True)).to(equal({
                'conf': True,
                'webhook': True
            }))

        with it(' must throw an exception when running the hook without args'):
            expect(test_hook.run_hook).to(raise_error(EnvironmentError))

        with it(' must return TRUE and HookName when running the hook with args'):
            expect(test_hook.run_hook(True)).to(equal(
                (True, test_hook.title)
            ))
    with context('Getting context-specific Hooks'):
        with it(' must return an empty list without Hooks loaded'):
            expect(get_hooks()).to(equal([]))

        with it('Must return TestHook when no context specified'):
            with patch('hookshub.plugins.PluginManager.get_hooks') as hooks_get:
                hook_data = namedtuple(
                    'TestHookNamedTuple',
                    'name, hook, event, repository, branch'
                )
                hook_data.name = test_hook.title
                hook_data.hook = test_hook
                hook_data.event = test_hook.event
                hook_data.repository = test_hook.repository
                hook_data.branch = test_hook.branch
                hooks_get.return_value = [hook_data]
                expect(get_hooks()).to(equal(
                    [(hook_data.name, hook_data.hook)]))

        with it(' must return TestHook2 when context specified'):
            class TestHook2(Hook):
                __module__ = 'hookshub.spec.format_plugins_spec'
                __version__ = _TEST_HOOK_VERSION

                def __init__(self):
                    super(TestHook2, self).__init__(
                        method=ok, repository='test_repo', branch='test',
                        event=GitHubUtil.events['EVENT_PULL_REQUEST']
                    )
            test_hook2 = TestHook2()
            with patch('hookshub.plugins.PluginManager.get_hooks') as hooks_get:
                hook_data = namedtuple(
                    'TestHookNamedTuple',
                    'name, hook, event, repository, branch'
                )
                hook_data.name = test_hook2.title
                hook_data.hook = test_hook2
                hook_data.event = test_hook2.event
                hook_data.repository = test_hook2.repository
                hook_data.branch = test_hook2.branch
                hooks_get.return_value = [hook_data]
                expect(get_hooks(event=GitHubUtil.events['EVENT_PULL_REQUEST'],
                                 repository='test_repo', branch='test')).to(
                    equal([(hook_data.name, hook_data.hook)]))
