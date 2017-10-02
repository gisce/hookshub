from hookshub.plugins import PluginManager
from hookshub.hook import Hook
from hookshub.hooks.github import GitHubUtil

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
